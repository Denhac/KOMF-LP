# Python includes
import logging, os, sys

# Flask and other third-party includes
from logging.handlers import RotatingFileHandler
from flask import Flask, request, session, render_template, redirect, url_for, abort, send_from_directory, jsonify
from werkzeug import secure_filename

# Our own includes
import envproperties
from DenhacJsonLib import JsonTools
from DenhacErrorLib import *

# Start 'er up
app = Flask(__name__)

####################################################################################
###### Debug is only invoked when run from the command-line for testing:
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)

####################################################################################
##### Application config values
####################################################################################
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024   # 1GB

####################################################################################
###### Key that is used to encrypt the session cookies (if we store things in session[])
#app.secret_key = envproperties.session_key
####################################################################################
###### Setting up the formatter for the log file
####################################################################################
if app.debug is not True:
	file_handler = RotatingFileHandler('/var/www/log/apifunctions.log', maxBytes=1024 * 1024 * 100, backupCount=20)
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
	if os.path.isfile(abs_path):
		return send_from_directory(os.path.dirname(abs_path), os.path.basename(abs_path))

	fileList = list()
	dirList  = list()
	for fileName in os.listdir(abs_path):
		if os.path.isdir(os.path.join(abs_path, fileName)):
			dirList.append(fileName)
		else:
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
