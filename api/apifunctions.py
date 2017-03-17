# Python includes
import logging, os, sys, urllib2
from threading import Thread

# Flask and other third-party includes
from logging.handlers import RotatingFileHandler
from flask import Flask, request, session, render_template, redirect, url_for, abort, send_from_directory, jsonify
from werkzeug import secure_filename, check_password_hash
#from flask_cors import CORS, cross_origin

# Our own includes
import envproperties
from DenhacDbLib import DenhacDb, DenhacRadioDjDb
from DenhacJsonLib import JsonTools
from DenhacErrorLib import *
from DenhacEmailLibrary import *

# Start 'er up
app = Flask(__name__)
#CORS(app)

####################################################################################
###### Debug is only invoked when run from the command-line for testing:
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)

####################################################################################
###### Used to encrypt the session cookies
app.secret_key = envproperties.session_key

####################################################################################
##### Application config values
####################################################################################
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024   # 1GB

####################################################################################
###### Setting up the formatter for the log file
####################################################################################
if app.debug is not True:
	file_handler = RotatingFileHandler(envproperties.API_LOG_FILE, maxBytes=1024 * 1024 * 100, backupCount=20)
	file_handler.setLevel(logging.ERROR)
	formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
	file_handler.setFormatter(formatter)
	app.logger.addHandler(file_handler)

####################################################################################
# Custom error handlers
####################################################################################
# HTTP 400 - Bad Request
@app.errorhandler(BadRequestException)
def bad_request_error(e):
	return JsonTools.Reply(e.to_dict()), 400

# HTTP 404 - Not Found
@app.errorhandler(404)
@app.errorhandler(NotFoundException)
def not_found_exception(e):
	return JsonTools.Reply(dict(error = "File or Directory Not Found.")), 404

# HTTP 405 - Method Not Allowed
@app.errorhandler(405)
@app.errorhandler(MethodNotAllowedException)
def method_not_allowed_exception(e):
	return JsonTools.Reply(dict(error = "The method is not allowed for the requested URL.")), 405

# HTTP 500 - Internal Server Error
@app.errorhandler(500)
@app.errorhandler(InternalServerErrorException)
def internal_server_error(e):
	app.logger.error(e)
	if type(e) is not InternalServerErrorException:
		e = InternalServerErrorException("Unknown Error. Check log file for details.")
	return JsonTools.Reply(e.to_dict()), 500

####################################################################################
#     QUICK TESTER SERVICES
####################################################################################

# Hello world tester
@app.route("/helloworld")
def helloworld():
	return JsonTools.Reply(dict(msg = "Hello, cruel world!"))

# Error tester
@app.route("/errortester")
def errortester():
	raise InternalServerErrorException(error = "DOH! You screwed up!")

# Generic exception tester
@app.route("/exceptiontester")
def exceptiontester():
	raise Exception("DOH! You screwed up generically!")

# Logging tester
@app.route("/logtester")
def logtester():
	app.logger.error("LOG TEST")
	return JsonTools.Reply(dict(msg = "Success"))

####################################################################################
#     SERVICE DEFINITIONS
####################################################################################

# The empty endpoint shows you the login page
@app.route('/')
def main():
	return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
	username = None
	password = None

	try:
		if request.method == 'POST':
			# Will throw KeyError if vars not present
#			username = request.form['username']
			password = request.form['password']

#		if not username or not password:			# Detect the condition if a var is there but empty
		if not password:
			raise KeyError

		# Check the input password against the configured hash value
		if not check_password_hash(envproperties.komf_password_hash, password):
			raise KeyError

	except KeyError:
		raise BadRequestException(error="Valid Username and Password are required!")

	session['logged_in'] = True
	session['hash_pw']   = envproperties.komf_password_hash

	return redirect(url_for('internalpages'))

@app.route('/internalpages', methods=['GET'])
def internalpages():
	if not checkPassword():
		return redirect(url_for('main'))
	return render_template('internalpages.html')

@app.route('/logout', methods=['GET'])
def logout():
	if 'logged_in' in session:
		del session['logged_in']

	if 'hash_pw' in session:
		del session['hash_pw']

	return redirect(url_for('main'))

# Helper fn to avoid lots of repeated code
def validatepath(dir, filepath):
	abs_path = os.path.join(dir, filepath).strip()
	# No, you can't inject a relative path, you get 404 instead
	if '..' in abs_path:
		raise NotFoundException()
	if not os.path.isdir(abs_path) and not os.path.isfile(abs_path):
		raise NotFoundException()
	return abs_path

# Generic read-and-download-anything-under-my-defined-base service
### NOTE: ALL subdirectories in this tree must have permissions 755 for this to be readable!
@app.route('/files', defaults={'filepath':''})
@app.route('/files/<path:filepath>')
def getfiles(filepath):
	abs_path = validatepath(envproperties.BASE_HOSTING_DIR, filepath)

	# If a file, ok stream it to the client (use specifically send_from_directory()) to avoid memory caps)
	# TODO - should probably test that sometime.  Server has 2G I think, but will we have any mp3s that big anyway?  Nope; max on DOM site is 100MB anyway.
	if os.path.isfile(abs_path):
		return send_from_directory(os.path.dirname(abs_path), os.path.basename(abs_path))

	fileList = list()
	dirList  = list()
	for fileName in os.listdir(abs_path):
		if os.path.isdir(os.path.join(abs_path, fileName)):
			dirList.append(fileName)
		else:
			# Exclude metadata files; they're implicit
			if not fileName.endswith('.metadata'):
				fileList.append(fileName)

	return JsonTools.Reply(dict(files = fileList, subdirs = dirList))

@app.route('/uploadpublic', methods=['GET', 'POST'])
def upload_file_public():
	# If post, they're sending us the file.  Save the file and its associated metadata
	if request.method == 'POST':
		return upload_file(envproperties.UPLOAD_PUBLIC_FOLDER)

	# Else it's GET, so show them the Upload form (test form for now)
	# TODO - replace this with a template that mirrors the DOM member content submission page
	# But this works fine for testing for now
	return '''
	<!doctype html>
	<title>Upload new File</title>
	<h1>Upload new File</h1>
	<form action="" method=post enctype=multipart/form-data>
		<p><input type=file name=file>
		 <input type=submit value=Upload>
	</form>
	'''

@app.route('/uploadstaging', methods=['GET', 'POST'])
def upload_file_staging():
	# If post, they're sending us the file, so save it
	if request.method == 'POST':
		return upload_file(envproperties.UPLOAD_STAGING_FOLDER)

	# Else it's GET, so show them the Upload form (test form for now)
	# TODO - replace this with a template that mirrors the DOM member content submission page
	# But this works fine for testing for now
	return '''
	<!doctype html>
	<title>Upload new File</title>
	<h1>Upload new File</h1>
	<form action="" method=post enctype=multipart/form-data>
		<p><input type=file name=file>
		 <input type=submit value=Upload>
	</form>
	'''

# This helper function makes upload_file() a lot more readable.
# It checks the input file type against allowed values.
# With thanks to http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in envproperties.ALLOWED_EXTENSIONS

def upload_file(folder):
	file = request.files['file']
	filename = secure_filename(file.filename)
	if file and allowed_file(file.filename):
		app.config['UPLOAD_FOLDER'] = folder
		file.save(os.path.join(folder, filename))
		return JsonTools.Reply(dict(success = "True"))
	else:
		raise BadRequestException(error="Not a valid file type.", payload=dict(filename = filename))

@app.route('/setmetadata/<path:filepath>', methods=['POST'])
def set_metadata(filepath):
	abs_path = validatepath(envproperties.BASE_HOSTING_DIR, filepath)
	abs_path = abs_path + ".metadata"

	# Check that we have json data POSTed
	formdata = request.get_json()
	if formdata is None or formdata == '':
		raise BadRequestException(error="Metadata in JSON format is required.")

	# TODO - check formdata[] for required fields here

	# Assuming we have all required fields, write the metadata to the filesystem
	metadata_file = open(abs_path, 'w')
	metadata_file.write(str(formdata))
	metadata_file.close()

	return JsonTools.Reply(dict(success = "True"))

@app.route('/movetolibrary/<dirname>/<filename>', methods=['GET'])
def move_to_library(dirname, filename):
	fullpath = validatepath(os.path.join(envproperties.BASE_HOSTING_DIR, dirname), filename)

	# Check for metadata and fail if not exists
	if not os.path.isfile(fullpath + ".metadata"):
		raise BadRequestException("A .metadata file is required in order to move a file to library.")

	# Move both the file and the metadata
	os.rename(fullpath,               os.path.join(envproperties.UPLOAD_LIBRARY_FOLDER, filename))
	os.rename(fullpath + '.metadata', os.path.join(envproperties.UPLOAD_LIBRARY_FOLDER, filename + '.metadata'))

	return JsonTools.Reply(dict(success = "True"))

@app.route('/themeblocktotals')
def themeblocktotals():
	radioDj = DenhacRadioDjDb()

	themeblocksEnabled  = radioDj.getThemeblockEnabledTotals()
	themeblocksDisabled = radioDj.getThemeblockDisabledTotals()
	genresEnabled       = radioDj.getGenreEnabledTotals()
	genresDisabled      = radioDj.getGenreDisabledTotals()
	enableds            = radioDj.getEnabledTotals()
	unknowns            = radioDj.getUnknownSongs()

	return render_template('themeblocktotals.html', themeblocksEnabled = themeblocksEnabled, themeblocksDisabled = themeblocksDisabled, genresEnabled = genresEnabled, genresDisabled = genresDisabled, enableds=enableds, unknowns=unknowns)

def checkPassword():

	if 'logged_in' not in session or not session['logged_in']:
		app.logger.error('First is true')
		return False

	if 'hash_pw'   not in session or session['hash_pw'] != envproperties.komf_password_hash:
		app.logger.error('Second is true')
		return False

	return True

@app.route('/updateschedules', methods=['GET', 'POST'])
def updateschedules():

	if not checkPassword():
		return redirect(url_for('main'))

	# If GET, then show the form displaying current values in the table
	if request.method == 'GET':
		radioDj   = DenhacRadioDjDb()
		rows      = radioDj.getSchedules()
		schedules = radioDj.getVerifiedSchedules()
		return render_template('updateschedules.html', rows = rows, schedules = schedules)

	# Else if POST, then save the update and reload the form
	project     = ""
	day         = ""
	time_string = ""

	if 'project' in request.form:
		project     = request.form['project']
	if 'day' in request.form:
		day         = request.form['day']

#	try:
	time_string = request.form['hour'] + ':' + request.form['minute']
#	except KeyError:
#		return DenhacJsonLibrary.ReplyWithError("Hour and Minute are required!")

	radioDj = DenhacRadioDjDb()
	radioDj.upsertSchedule(None, project, day, time_string)
	rows = radioDj.getSchedules()
	return redirect(url_for('updateschedules'))

@app.route('/deleteschedule/<playlist_id>', methods=['GET'])
def deleteschedule(playlist_id):
	if not checkPassword():
		return redirect(url_for('main'))

	radioDj = DenhacRadioDjDb()
	radioDj.deleteSchedule(playlist_id)
	return redirect(url_for('updateschedules'))

@app.route('/viewrotationschedule', methods=['GET'])
def viewrotationschedule():
	if not checkPassword():
		return redirect(url_for('main'))

	radioDj       = DenhacRadioDjDb()
	rows          = radioDj.getRotationSchedules()
	themeblocks   = radioDj.getThemeBlocksForUserSelection()
	verifications = radioDj.getRotationVerification()

	return render_template('viewrotationschedule.html', rows = rows, themeblocks = themeblocks, verifications = verifications)

@app.route('/deleterotationschedule/<rotation_id>', methods=['GET'])
def deleterotationschedule(rotation_id):
	if not checkPassword():
		return redirect(url_for('main'))

	radioDj = DenhacRadioDjDb()
	radioDj.deleteRotationSchedule(rotation_id)
	radioDj.updateAutoRotation()
	return redirect(url_for('viewrotationschedule'))

@app.route('/addrotationschedule', methods=['POST'])
def addrotationschedule():
	if not checkPassword():
		return redirect(url_for('main'))

	rotationname   = request.form['rotationname']
	hour           = request.form['hour']
	minute         = request.form['minute']
	themeblockid   = request.form['themeblockid']
	kickofftrackid = request.form['kickofftrackid']
	days           = str('&0' if 'Sunday'    in request.form else '')
	days		  += str('&1' if 'Monday'    in request.form else '')
	days		  += str('&2' if 'Tuesday'   in request.form else '')
	days		  += str('&3' if 'Wednesday' in request.form else '')
	days		  += str('&4' if 'Thursday'  in request.form else '')
	days		  += str('&5' if 'Friday'    in request.form else '')
	days		  += str('&6' if 'Saturday'  in request.form else '')

	radioDj = DenhacRadioDjDb()
	radioDj.addRotationSchedule(rotationname, hour + ':' + minute + ':00', themeblockid, days, kickofftrackid)
	radioDj.updateAutoRotation()

	return redirect(url_for('viewrotationschedule'))

@app.route('/manageinternalcontent', methods=['GET'])
def manageinternalcontent():
	if not checkPassword():
		return redirect(url_for('main'))

	radioDj = DenhacRadioDjDb()
	tracks  = radioDj.getKomfTrackSummary()
	return render_template('manageinternalcontent.html', tracks = tracks)

@app.route('/nowplaying', methods=['POST'])
def nowplaying():
	# Check for required fields
	if 'track' not in request.form or 'artist' not in request.form or 'album' not in request.form or 'playlistServiceToken' not in request.form:
		raise BadRequestException(error="track, artist, album, and playlistServiceToken are required POST vars")

	if request.form['playlistServiceToken'] != 'eggsmayhem':
		raise BadRequestException(error="Invalid playlistServiceToken")

	# Ignore notifications for Outros
	if request.form['track'].endswith('- OUTRO'):
		return JsonTools.Reply(dict(msg = "Success"))

	# Start one background worker for each target that wants to receive a notification
	# (This way RadioDJ doesn't have to wait on a response if any remote system has any issues; it just rotates and continues.)
	thread = Thread(target=background_call_radiorethink, args=[request.form])
	thread.start()

	## thread2 = Thread(target=background_call_omf_website.... etc)
	## thread2.start()
	## etc

	return JsonTools.Reply(dict(msg = "Success"))

def background_call_radiorethink(vars):
	url  = "http://radiorethink.com/playlistService/incoming.cfm?stationCode=KOMF"

	if 'playlistServiceToken' in vars:
		url += "&playlistServiceToken=v3hamjBtzwYcgJ7u"
	if 'artist' in vars:
		url += "&artist=" + urllib2.quote(vars['artist'])
	if 'track' in vars:
		url += "&track=" + urllib2.quote(vars['track'])
	if 'album' in vars:
		url += "&album=" + urllib2.quote(vars['album'])
	if 'showID' in vars:
		url += "&showID=" + urllib2.quote(vars['showID'])
	if 'songID' in vars:
		url += "&songID=" + urllib2.quote(vars['songID'])
#	if 'playlistID' in vars:
#		url += "&playlistID="
#	if 'trackTimestamp' in vars:
#		url += "&trackTimestamp="
	if 'showName' in vars:
		url += "&showName=" + urllib2.quote(vars['showName'])
#	if 'showHost' in vars:
#		url += "&showHost="

	try:
		app.logger.error("Calling RadioRethink URL: " + url)
		urllib2.urlopen(url = url, data = None, timeout = 60)

	except:
		exType, value, traceback = sys.exc_info()
		app.logger.error(str(value))
		DenhacEmail.SendEmail(fromAddr = 'autobot@denhac.org',
							  toAddr   = ['anthony.stonaker@gmail.com'],
							  subject  = 'Callout to RadioRethink failed',
							  body     = 'Type:  ' + str(exType) + '\n' +
							  			 'Value: ' + str(value) + '\n' +
							  			 'Trace: ' + str(traceback))