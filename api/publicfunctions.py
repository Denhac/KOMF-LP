# Python includes
import logging, os, sys

# Flask and other third-party includes
from logging.handlers import RotatingFileHandler
from flask import Flask, request, session, render_template, redirect, url_for, abort, send_from_directory, jsonify
from werkzeug import secure_filename

# Our own includes
import envproperties
from DenhacDbLib import DenhacDb, DenhacRadioDjDb
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

@app.route('/viewscheduledshowverification', methods=['GET'])
def viewscheduledshowverification():
    radioDj = DenhacRadioDjDb()
    rows    = radioDj.getScheduledShowVerification()

    return render_template('viewscheduledshowverification.html', rows = rows)

@app.route('/rotationschedule', methods=['GET'])
def rotationschedule():
    radioDj       = DenhacRadioDjDb()
    rows          = radioDj.getRotationSchedules()

    return JsonTools.Reply(dict(schedules = rows))
