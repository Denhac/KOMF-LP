# -*- coding: utf-8 -*-

# Python includes
import base64, json, logging, os, sys, urllib2
from datetime import datetime
from threading import Thread
import socket

# Flask and other third-party includes
from logging.handlers import RotatingFileHandler
from flask import Flask, request, session, render_template, redirect, url_for, send_from_directory
from werkzeug import secure_filename, check_password_hash
#from flask_cors import CORS, cross_origin
import eyed3

# Our own includes
import envproperties
from DenhacDbLib import DenhacDb, DenhacRadioDjDb
from DenhacErrorLib import *
from DenhacEmailLibrary import *
from DenhacJsonLib import JsonTools
from DenhacRadioSongLib import RadioSongLib

# Start 'er up
app = Flask(__name__)

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
    app.logger.setLevel(logging.DEBUG)
    file_handler = RotatingFileHandler(envproperties.API_LOG_FILE, maxBytes=1024 * 1024 * 100, backupCount=20)
    file_handler.setLevel(logging.DEBUG)
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
    return JsonTools.Reply(dict(error="File or Directory Not Found.")), 404

# HTTP 405 - Method Not Allowed
@app.errorhandler(405)
@app.errorhandler(MethodNotAllowedException)
def method_not_allowed_exception(e):
    return JsonTools.Reply(dict(error="The method is not allowed for the requested URL.")), 405

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
    return JsonTools.Reply(dict(msg="Hello, cruel world!"))

# Error tester
@app.route("/errortester")
def errortester():
    raise InternalServerErrorException(error="DOH! You screwed up!")

# Generic exception tester
@app.route("/exceptiontester")
def exceptiontester():
    raise Exception("DOH! You screwed up generically!")

# Logging tester
@app.route("/logtester")
def logtester():
    app.logger.debug("LOG TEST")
    return JsonTools.Reply(dict(msg="Success"))

####################################################################################
#     SERVICE DEFINITIONS
####################################################################################

# The empty endpoint shows you the login page
@app.route('/')
def main():
    return render_template('login.html', envproperties=envproperties)

@app.route('/login', methods=['POST'])
def login():
    username = None
    password = None

    try:
        if request.method == 'POST':
            # Will throw KeyError if vars not present
#            username = request.form['username']
            password = request.form['password']

#        if not username or not password:            # Detect the condition if a var is there but empty
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

    radioDj = DenhacRadioDjDb()
    row = radioDj.getLastImportDatetime()[0]
    return render_template('internalpages.html', row=row, envproperties=envproperties)

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

    return JsonTools.Reply(dict(files=fileList, subdirs=dirList))

@app.route('/uploadpublic', methods=['GET', 'POST'])
def upload_file_public():
    # If post, they're sending us the file.  Save the file and its associated metadata
    if request.method == 'POST':
#        return upload_file(envproperties.UPLOAD_PUBLIC_FOLDER)
        if upload_file(envproperties.UPLOAD_PUBLIC_FOLDER):
            return JsonTools.Reply(dict(success="True"))

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
#        return upload_file(envproperties.UPLOAD_STAGING_FOLDER)
        if upload_file(envproperties.UPLOAD_STAGING_FOLDER):
            return JsonTools.Reply(dict(success="True"))

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

@app.route('/uploadinternal', methods=['POST'])
def upload_file_internal():
    genre = 60
    song_type, id_subcat = 0, 0
    content_type = request.form['content_type']

    if content_type == 'Underwriting':
        song_type, id_subcat, prefix = 4, 17, 'Underwriting'
    elif content_type == 'Sweeper':
        song_type, id_subcat, prefix = 2, 12, 'Sweeper'
    elif content_type == 'KUVO Station ID':
        song_type, id_subcat, prefix = 2, 15, 'KUVO_Station_ID'
    elif content_type == 'KUVO + K225BS Station ID':
        song_type, id_subcat, prefix = 2, 16, 'KUVO_K225BS_Station_ID'
    elif content_type == 'PSA':
        song_type, id_subcat, prefix = 4, 20, 'PSA'
    elif content_type == 'Other':
        song_type, id_subcat, prefix = 6, 11, 'Other'
    else:
        raise BadRequestException(error="Not a valid content_type.", payload=dict(content_type=content_type))

    upload_path = "%s/internalcontent/%s" % (envproperties.UPLOAD_LIBRARY_FOLDER, prefix)
    if not upload_file(upload_path):
        raise InternalServerErrorException(error="File upload failed! Check server log file.")

    file = request.files['file']
    filename = secure_filename(file.filename)
    full_path = os.path.join(upload_path, filename)
    duration = RadioSongLib.getDurationFromFile(full_path)
    frontend_path = "%s\\internalcontent\\%s\\%s" % (envproperties.RADIODJ_CLIENT_FOLDER, prefix, filename)
    cue_times = RadioSongLib.getCueTimesFromDuration(duration)

    eyed3.log.setLevel("ERROR")
    audiofile = eyed3.load(full_path)
    tag = audiofile.tag

    artist = 'Default Artist'
    album = 'Default Album'

    if tag is not None:
        if tag.artist is not None:
            artist = tag.artist
        if tag.album is not None:
            album = tag.album

    today = datetime.today()
    year = today.year

    radioDj = DenhacRadioDjDb()
    radioDj.upsertSongs(frontend_path,
                        song_type=song_type,
                        id_subcat=id_subcat,
                        id_genre=genre,
                        duration=duration,
                        artist=artist,
                        album=album,
                        year=year,
                        copyright='',
                        title=filename,
                        publisher='',
                        composer='',
                        cue_times=cue_times,
                        enabled=1,
                        comments='',
                        play_limit=0,
                        limit_action=0)

#    return JsonTools.Reply(dict(content_type=content_type, song_type=song_type, id_subcat=id_subcat, prefix=prefix,
#                                upload_path=upload_path, duration=duration, full_path=full_path,
#                                frontend_path=frontend_path, cue_times=cue_times))
    return redirect(url_for('manageinternalcontent'))

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
        return JsonTools.Reply(dict(success="True"))
    else:
        raise BadRequestException(error="Not a valid file type.", payload=dict(filename = filename))

@app.route('/setmetadata/<path:filepath>', methods=['POST'])
def set_metadata(filepath):
    validatepath(envproperties.BASE_HOSTING_DIR, filepath)

    # Check that we have json data POSTed
    formdata = request.get_json()
    if formdata is None or formdata == '':
        raise BadRequestException(error="Metadata in JSON format is required.")

    if 'title' not in formdata:
        raise BadRequestException(error="title is a required field.")

    if 'broadcastFlag' in formdata and formdata['broadcastFlag'] == 'Yes':
        if 'theme' not in formdata or 'genre' not in formdata or 'artist' not in formdata or 'broadcastFlag' not in formdata or 'indecencyFlag' not in formdata:
            raise BadRequestException(error="title, theme, genre, artist, broadcastFlag, indecencyFlag are required fields when broadcastFlag='Yes'.")

    # Ok, the file exists and we know we have the required fields.  Save the transaction so the new import job can pick it up.
    radioDj = DenhacRadioDjDb()
    radioDj.addSetMetadata(json.dumps(formdata))

    return JsonTools.Reply(dict(success="True"))

@app.route('/movetolibrary/<dirname>/<filename>', methods=['GET'])
def move_to_library(dirname, filename):
    fullpath = validatepath(os.path.join(envproperties.BASE_HOSTING_DIR, dirname), filename)

    # Check for metadata and fail if not exists
    if not os.path.isfile(fullpath + ".metadata"):
        raise BadRequestException("A .metadata file is required in order to move a file to library.")

    # Move both the file and the metadata
    os.rename(fullpath,               os.path.join(envproperties.UPLOAD_LIBRARY_FOLDER, filename))
    os.rename(fullpath + '.metadata', os.path.join(envproperties.UPLOAD_LIBRARY_FOLDER, filename + '.metadata'))

    return JsonTools.Reply(dict(success="True"))

@app.route('/themeblocktotals')
def themeblocktotals():
    radioDj = DenhacRadioDjDb()

    themeblocksEnabled  = radioDj.getThemeblockEnabledTotals()
    themeblocksDisabled = radioDj.getThemeblockDisabledTotals()
    genresEnabled       = radioDj.getGenreEnabledTotals()
    genresDisabled      = radioDj.getGenreDisabledTotals()
    enableds            = radioDj.getEnabledTotals()
    unknowns            = radioDj.getUnknownSongs()

    return render_template('themeblocktotals.html', themeblocksEnabled = themeblocksEnabled, themeblocksDisabled = themeblocksDisabled, genresEnabled = genresEnabled, genresDisabled = genresDisabled, enableds=enableds, unknowns=unknowns, envproperties=envproperties)


def checkPassword():
    if 'logged_in' not in session or not session['logged_in']:
        app.logger.debug('First is true')
        return False

    if 'hash_pw' not in session or session['hash_pw'] != envproperties.komf_password_hash:
        app.logger.debug('Second is true')
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
        live_show_calendar = radioDj.getLiveShowCalendar()
        live_show_calendar_comment = radioDj.getTableComment('komf_live_show_calendar')
        komf_scheduled_shows_comment = radioDj.getTableComment('komf_scheduled_shows')
        komf_scheduled_show_verification_comment = radioDj.getViewComment('komf_scheduled_show_verification')

        return render_template('updateschedules.html',
                               rows=rows,
                               schedules=schedules,
                               live_show_calendar=live_show_calendar,
                               live_show_calendar_comment=live_show_calendar_comment, envproperties=envproperties,
                               komf_scheduled_shows_comment=komf_scheduled_shows_comment,
                               komf_scheduled_show_verification_comment=komf_scheduled_show_verification_comment)

    # Else if POST, then save the update and reload the form
    project     = ""
    day         = ""
    time_string = ""

    if 'project' in request.form:
        project     = request.form['project']
    if 'day' in request.form:
        day         = request.form['day']

    time_string = request.form['hour'] + ':' + request.form['minute']
    show_length_string = request.form['showlengthhour'] + ':' + request.form['showlengthminute'] + ':00'

    radioDj = DenhacRadioDjDb()
    radioDj.upsertSchedule(None, project, day, time_string, show_length_string)
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

    radioDj = DenhacRadioDjDb()
    rows = radioDj.getRotationSchedules()
    themeblocks = radioDj.getThemeBlocksForUserSelection()
    verifications = radioDj.getRotationVerification()

    hits_rotation_criteria = radioDj.getHitsRotationCriteria()
    rotation_criteria = radioDj.getRotationCriteria()
    content_hours_per_week = radioDj.getContentHoursPerWeek()
    rotation_ranking = radioDj.getRotationRanking()
    hits_rotation_ranking = radioDj.getHitsRotationRanking()

    komf_rotation_schedule_comment = radioDj.getTableComment('komf_rotation_schedule')
    komf_rotation_verification_comment = radioDj.getTableComment('komf_rotation_verification')
    komf_hits_rotation_criteria_comment = radioDj.getTableComment('komf_hits_rotation_criteria')
    komf_rotation_criteria_comment = radioDj.getTableComment('komf_rotation_criteria')
    komf_content_hours_per_week_comment = radioDj.getViewComment('komf_content_hours_per_week')
    komf_rotation_ranking_comment = radioDj.getViewComment('komf_rotation_ranking')
    komf_hits_rotation_ranking_comment = radioDj.getViewComment('komf_hits_rotation_ranking')

    return render_template('viewrotationschedule.html', rows=rows, themeblocks=themeblocks, verifications=verifications,
                           komf_rotation_schedule_comment=komf_rotation_schedule_comment,
                           komf_rotation_verification_comment=komf_rotation_verification_comment,
                           hits_rotation_criteria=hits_rotation_criteria, rotation_criteria=rotation_criteria,
                           content_hours_per_week=content_hours_per_week, rotation_ranking=rotation_ranking,
                           hits_rotation_ranking=hits_rotation_ranking,
                           komf_hits_rotation_criteria_comment=komf_hits_rotation_criteria_comment,
                           komf_rotation_criteria_comment=komf_rotation_criteria_comment,
                           komf_content_hours_per_week_comment=komf_content_hours_per_week_comment,
                           komf_rotation_ranking_comment=komf_rotation_ranking_comment,
                           komf_hits_rotation_ranking_comment=komf_hits_rotation_ranking_comment,
                           envproperties=envproperties)

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
    days          += str('&1' if 'Monday'    in request.form else '')
    days          += str('&2' if 'Tuesday'   in request.form else '')
    days          += str('&3' if 'Wednesday' in request.form else '')
    days          += str('&4' if 'Thursday'  in request.form else '')
    days          += str('&5' if 'Friday'    in request.form else '')
    days          += str('&6' if 'Saturday'  in request.form else '')

    radioDj = DenhacRadioDjDb()
    radioDj.addRotationSchedule(rotationname, hour + ':' + minute + ':00', themeblockid, days, kickofftrackid)
    radioDj.updateAutoRotation()

    return redirect(url_for('viewrotationschedule'))


@app.route('/manageinternalcontent', methods=['GET'])
def manageinternalcontent():
    if not checkPassword():
        return redirect(url_for('main'))

    radioDj = DenhacRadioDjDb()
    tracks = radioDj.getKomfTrackSummary()
    komf_track_summary_comment = radioDj.getViewComment('komf_track_summary')

    return render_template('manageinternalcontent.html', tracks=tracks, envproperties=envproperties,
                           komf_track_summary_comment=komf_track_summary_comment)


@app.route('/nowplaying', methods=['POST'])
def nowplaying():
    # Check for required fields
    if 'track' not in request.form or 'artist' not in request.form or 'album' not in request.form or 'playlistServiceToken' not in request.form:
        raise BadRequestException(error="track, artist, album, and playlistServiceToken are required POST vars")

    if request.form['playlistServiceToken'] != 'eggsmayhem':
        raise BadRequestException(error="Invalid playlistServiceToken")

    # Ignore notifications for Outros
    if request.form['track'].endswith('- OUTRO'):
        return JsonTools.Reply(dict(msg="Success"))

    # https://github.com/Denhac/KOMF-LP/issues/23
    # Ignore anything with subcategory > 10
    radioDj = DenhacRadioDjDb()
    song_info = radioDj.getSongById(request.form['songID'])
    subcategory_id = song_info['id_subcat']
    if subcategory_id > 10:
        app.logger.info(msg="Subcategory is %s. Ignoring for rotation purposes." % subcategory_id)
        return JsonTools.Reply(dict(msg="Success"))
    # End #23

    # Start one background worker for each target that wants to receive a notification
    # (This way RadioDJ doesn't have to wait on a response if any remote system has any issues; it just rotates and continues.)
    if envproperties.send_to_radiorethink:
        thread = Thread(target=background_call_radiorethink, args=[request.form])
        thread.start()

    if envproperties.send_to_icecast:
        thread2 = Thread(target=background_call_icecast, args=[request.form])
        thread2.start()

    if envproperties.send_to_kuvo:
        thread3 = Thread(target=background_call_kuvo, args=[request.form])
        thread3.start()

    if envproperties.send_to_kuvo_hd3:
        thread4 = Thread(target=background_call_kuvo_hd3, args=[request.form])
        thread4.start()

    return JsonTools.Reply(dict(msg="Success"))


def background_call_radiorethink(vars):
    url = envproperties.radiorethink_url

    radioDj = DenhacRadioDjDb()
    extended_info = radioDj.getSongExtended(vars['songID'])

    if 'playlistServiceToken' in vars:
        url += "&playlistServiceToken=" + envproperties.playlist_service_token
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
#    if 'playlistID' in vars:
#        url += "&playlistID="
#    if 'trackTimestamp' in vars:
#        url += "&trackTimestamp="
    if 'showName' in vars:
        url += "&showName=" + urllib2.quote(vars['showName'])
#    if 'showHost' in vars:
#        url += "&showHost="
    if 'album_art' in extended_info and len(extended_info['album_art']) > 0:
        url += "&trackImage=" + urllib2.quote(extended_info['album_art'], '')
    if 'show_link' in extended_info and len(extended_info['show_link']) > 0:
        url += "&detailUrl=" + urllib2.quote(extended_info['show_link'], '')

    try:
        app.logger.debug("Calling RadioRethink URL: %s" % url)
        urllib2.urlopen(url=url, data=None, timeout=60)
        app.logger.info("Successfully rotated RadioRethink metadata.")

    except:
        exType, value, traceback = sys.exc_info()
        app.logger.error(str(value))
        DenhacEmail.SendEmail(fromAddr=envproperties.ERROR_FROM_EMAIL,
                              toAddr=envproperties.ERROR_TO_EMAIL_LIST,
                              subject='Callout to RadioRethink failed',
                              body='Type:  ' + str(exType) + '\n' +
                                   'Value: ' + str(value) + '\n' +
                                   'Trace: ' + str(traceback))


def background_call_icecast(vars):
    if 'track' not in vars:
        app.logger.info("No track data to send to Icecast.")
        return

    get_vars = 'mount=/stream&mode=updinfo&song='

    if 'artist' in vars and 'unknown' not in vars['artist'].lower():
        get_vars += urllib2.quote(vars['artist'].replace('-', ''))

    get_vars += urllib2.quote(' - ' + vars['track'].replace('-', ''))

    url = envproperties.icecast_url + '?' + get_vars

    try:
        app.logger.debug("Calling Icecast URL: " + url)

        req = urllib2.Request(url)
        b64auth = base64.standard_b64encode("%s:%s" % (envproperties.icecast_user, envproperties.icecast_password))
        req.add_header("Authorization", "Basic %s" % b64auth)
        urllib2.urlopen(req)

        app.logger.info("Successfully rotated Icecast metadata.")

    except:
        exType, value, traceback = sys.exc_info()
        app.logger.error(str(value))

        message_body = 'Type:  ' + str(exType) + '\n' +\
                       'Value: ' + str(value) + '\n' +\
                       'Trace: ' + str(traceback) + '\n'

        DenhacEmail.SendEmail(fromAddr=envproperties.ERROR_FROM_EMAIL,
                              toAddr=envproperties.ERROR_TO_EMAIL_LIST,
                              subject='Callout to Icecast failed',
                              body=message_body)


def background_call_kuvo(vars):
    if 'track' not in vars:
        app.logger.info("No track data to send to KUVO.")
        return

    post_vars = "track=%s" % vars['track'].replace('&', '&amp;')

    if 'artist' in vars and 'unknown' not in vars['artist'].lower():
        post_vars += "&artist=%s" % vars['artist'].replace('&', '&amp;')

    try:
        app.logger.debug("KUVO post_vars: %s" % post_vars)
        app.logger.debug("Calling KUVO URL: %s" % envproperties.kuvo_url)

        ip, port = envproperties.kuvo_url.split(':')
        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.sendto(post_vars, (ip, int(port)))
        app.logger.info("Successfully rotated KUVO metadata.")

    except:
        exType, value, traceback = sys.exc_info()
        app.logger.error(str(value))
        DenhacEmail.SendEmail(fromAddr=envproperties.ERROR_FROM_EMAIL,
                              toAddr=envproperties.ERROR_TO_EMAIL_LIST,
                              subject='Callout to KUVO failed',
                              body='Type:  ' + str(exType) + '\n' +
                                   'Value: ' + str(value) + '\n' +
                                   'Trace: ' + str(traceback))


def background_call_kuvo_hd3(vars):
    if 'track' not in vars:
        app.logger.info("No track data to send to KUVO HD3.")
        return

    post_vars = "track=%s" % vars['track'].replace('&', '&amp;')

    if 'artist' in vars and 'unknown' not in vars['artist'].lower():
        post_vars += "&artist=%s" % vars['artist'].replace('&', '&amp;')

    try:
        app.logger.debug("KUVO HD3 post_vars: %s" % post_vars)
        app.logger.debug("Calling KUVO HD3 URL: %s" % envproperties.kuvo_hd3_url)

        ip, port = envproperties.kuvo_hd3_url.split(':')
        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.sendto(post_vars, (ip, int(port)))
        app.logger.info("Successfully rotated KUVO HD3 metadata.")

    except:
        exType, value, traceback = sys.exc_info()
        app.logger.error(str(value))
        DenhacEmail.SendEmail(fromAddr=envproperties.ERROR_FROM_EMAIL,
                              toAddr=envproperties.ERROR_TO_EMAIL_LIST,
                              subject='Callout to KUVO HD3 failed',
                              body='Type:  ' + str(exType) + '\n' +
                                   'Value: ' + str(value) + '\n' +
                                   'Trace: ' + str(traceback))


@app.route('/viewsongimportfailures', methods=['GET'])
def viewsongimportfailures():
    if not checkPassword():
        return redirect(url_for('main'))

    radioDj = DenhacRadioDjDb()
    rows = radioDj.getSongImportFailures()

    decodedrows = []
    for row in rows:
        newRow = {
            "song_title": str(row['song_title']).decode("utf-8"),
            "song_link": str(row['song_link']).decode("utf-8"),
            "error_type": row['error_type'],
            "error_message": row['error_message']
        }
        decodedrows.append(newRow)

    return render_template('songimportfailures.html', rows=decodedrows, envproperties=envproperties)

@app.route('/managecalendars', methods=['GET'])
def managecalendars():
    if not checkPassword():
        return redirect(url_for('main'))

    radioDj = DenhacRadioDjDb()
    consolidated_active_calendar = radioDj.getConsolidatedActiveCalendar()
    consolidated_active_calendar_comment = radioDj.getViewComment('komf_consolidated_active_calendar')
    active_live_show_calendar = radioDj.getActiveLiveShowCalendar()
    active_live_show_calendar_comment = radioDj.getViewComment('komf_active_live_show_calendar')
    active_prerecorded_show_calendar = radioDj.getActivePrerecordedShowCalendar()
    active_prerecorded_show_calendar_comment = radioDj.getViewComment('komf_active_prerec_show_calendar')
    active_rotation_calendar = radioDj.getActiveRotationCalendar()
    active_rotation_calendar_comment = radioDj.getViewComment('komf_active_rotation_calendar')
    live_show_calendar = radioDj.getLiveShowCalendar()
    live_show_calendar_comment = radioDj.getTableComment('komf_live_show_calendar')

    return render_template('managecalendars.html', consolidated_active_calendar=consolidated_active_calendar,
                           consolidated_active_calendar_comment=consolidated_active_calendar_comment,
                           active_live_show_calendar=active_live_show_calendar,
                           active_live_show_calendar_comment=active_live_show_calendar_comment,
                           active_prerecorded_show_calendar=active_prerecorded_show_calendar,
                           active_prerecorded_show_calendar_comment=active_prerecorded_show_calendar_comment,
                           active_rotation_calendar=active_rotation_calendar,
                           active_rotation_calendar_comment=active_rotation_calendar_comment,
                           live_show_calendar=live_show_calendar,
                           live_show_calendar_comment=live_show_calendar_comment, envproperties=envproperties
                           )

@app.route('/deleteliveshowcalendar/<time>', methods=['GET'])
def deleteliveshowcalendar(time):
    if not checkPassword():
        return redirect(url_for('main'))

    radioDj = DenhacRadioDjDb()
    radioDj.deleteLiveShowCalendar(time)
    return redirect(url_for('updateschedules'))

@app.route('/addliveshowcalendar', methods=['POST'])
def addliveshowcalendar():
    if not checkPassword():
        return redirect(url_for('main'))

    time = request.form['liveshowcalendarhour'] + ':' + request.form['liveshowcalendarminute'] + ':00'
    sunday = monday = tuesday = wednesday = thursday = friday = saturday = "None"

    if 'sunday' in request.form and request.form['sunday']:
        sunday = request.form['sunday']
    if 'monday' in request.form and request.form['monday']:
        monday = request.form['monday']
    if 'tuesday' in request.form and request.form['tuesday']:
        tuesday = request.form['tuesday']
    if 'wednesday' in request.form and request.form['wednesday']:
        wednesday = request.form['wednesday']
    if 'thursday' in request.form and request.form['thursday']:
        thursday = request.form['thursday']
    if 'friday' in request.form and request.form['friday']:
        friday = request.form['friday']
    if 'saturday' in request.form and request.form['saturday']:
        saturday = request.form['saturday']

    radioDj = DenhacRadioDjDb()
    radioDj.addLiveShowCalendar(time, sunday, monday, tuesday, wednesday, thursday, friday, saturday)
    return redirect(url_for('updateschedules'))

@app.route('/savehitsrotationcriteria', methods=['POST'])
def savehitsrotationcriteria():
    if not checkPassword():
        return redirect(url_for('main'))

    radioDj = DenhacRadioDjDb()
    radioDj.saveHitsRotationCriteria(request.form['min_bayesian'], request.form['avg_bayesian'],
                                     request.form['days_new'], request.form['new_weight'], request.form['days_old'],
                                     request.form['old_weight'], request.form['bays_if_zero'],
                                     request.form['no_repeat_hours'])
    return redirect(url_for('viewrotationschedule'))

@app.route('/saverotationcriteria', methods=['POST'])
def saverotationcriteria():
    if not checkPassword():
        return redirect(url_for('main'))

    radioDj = DenhacRadioDjDb()
    radioDj.saveRotationCriteria(request.form['min_bayesian'], request.form['avg_bayesian'],
                                 request.form['days_new'], request.form['new_weight'], request.form['days_old'],
                                 request.form['old_weight'], request.form['bays_if_zero'],
                                 request.form['no_repeat_hours'])
    return redirect(url_for('viewrotationschedule'))

@app.route('/viewserverapilogs', methods=['GET'])
def viewserverapilogs():
    if not checkPassword():
        return redirect(url_for('main'))

    with open(envproperties.API_LOG_FILE) as file:
        data = file.read()
        return render_template('viewserverapilogs.html', logs=data, envproperties=envproperties)

@app.route('/viewserverjoblogs', methods=['GET'])
def viewserverjoblogs():
    if not checkPassword():
        return redirect(url_for('main'))

    with open(envproperties.IMPORT_LOG_FILE) as file:
        data = file.read()
        return render_template('viewserverjoblogs.html', logs=data, envproperties=envproperties)
