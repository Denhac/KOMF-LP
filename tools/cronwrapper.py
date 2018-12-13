#!/usr/bin/python

# Python includes
import logging, logging.handlers, sys

# Our own package includes
# insert() makes our path the first searched entry, as opposed to append()
sys.path.insert(0, '/var/www/api')
from komfpackage import envproperties, DenhacEmail, DenhacDb, DenhacPidfile, DenhacRadioDjDb

######################################################################################
#           Global Objects
######################################################################################

# Set up Logging
appLogger = logging.getLogger('CronWrapper')
appLogger.propagate = False

# TODO - revert to INFO once we're stable
#appLogger.setLevel(logging.INFO)
appLogger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

handler = logging.handlers.RotatingFileHandler(envproperties.IMPORT_LOG_FILE, maxBytes=1024 * 1024 * 10, backupCount=20)
handler.setFormatter(formatter)

appLogger.addHandler(handler)

######################################################################################
# Set up DB object
radioDj = DenhacRadioDjDb()

######################################################################################
# Be certain that only one copy of this script can run at a time
try:
    DenhacPidfile.createPidFile()
except:
    exType, value, traceback = sys.exc_info()
    appLogger.error(str(value))
    exit(0)

######################################################################################
#           Main Script starts execution here
######################################################################################
appLogger.debug("==============================================")
appLogger.debug("Starting up, PID: " + str(DenhacPidfile.pid))
appLogger.debug("Running input script: " + sys.argv[1])

try:
    # Retrieve the SQL that was passed, wash it, and throw it at the DB
    radioDj.connect()
    sql = radioDj.escapeString(sys.argv[1])
    radioDj.executeQueryNoResult(sql, None)

    DenhacPidfile.removePidFile()
    appLogger.debug("Complete.")

except:
    appLogger.exception("Exception caught; aborting.")
    DenhacPidfile.removePidFile()

    exType, value, traceback = sys.exc_info()
    DenhacEmail.SendEmail(fromAddr = 'autobot@denhac.org',
                          toAddr   = ['anthony.stonaker@gmail.com'],
                          subject  = 'Cron Wrapper Script Failed',
                          body     = 'Type:  ' + str(exType) + '\n' +
                                       'Value: ' + str(value) + '\n' +
                                       'Trace: ' + str(traceback))