#!/usr/bin/python

# Python includes
import logging, logging.handlers, sys

# Our own package includes
# insert() makes our path the first searched entry, as opposed to append()
sys.path.insert(0, '/var/www/api')
from komfpackage import envproperties, DenhacEmail, DenhacDb, DenhacRadioDjDb

######################################################################################
#           Global Objects
######################################################################################

# Set up Logging
appLogger = logging.getLogger('ImportCheck')
appLogger.propagate = False

# TODO - revert to INFO once we're stable
#appLogger.setLevel(logging.INFO)
appLogger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

handler = logging.handlers.RotatingFileHandler(envproperties.IMPORT_LOG_FILE, maxBytes=1024 * 1024 * 10, backupCount=20)
handler.setFormatter(formatter)

appLogger.addHandler(handler)


######################################################################################
#           Main Script starts execution here
######################################################################################

try:
    appLogger.info("Starting import check.")

    # Get timestamps from DB
    radioDj = DenhacRadioDjDb()
    row = radioDj.getLastImportDatetime()[0]
    appLogger.debug("DB row: %s" % row)

    message = ""
    sendmsg = False

    if int(row['seconds_since_last_import']) > 24 * 60 * 60:     # 1 day
        sendmsg = True
        message += "More than 1 day elapsed since last successful .mp3 import from DOM portal: %s\n\n" % row['last_import_datetime']

    if int(row['seconds_since_last_maintenance']) > 24 * 60 * 60:     # 1 day
        sendmsg = True
        message += "More than 1 day elapsed since last successful maintenance (DB path fix and call RadioDJ refreshEvents service): %s" % row['last_maintenance_datetime']

    if sendmsg:
        appLogger.debug("sendmsg flag set.")
        DenhacEmail.SendEmail(fromAddr=envproperties.ERROR_FROM_EMAIL,
                              toAddr=envproperties.ERROR_IMPORT_CHECK_EMAIL_LIST,
                              subject='DOM Import Script Failure Detected (>24 hr)',
                              body=message)

    appLogger.info("Import check complete.")

except:
    e, v, t = sys.exc_info()
    appLogger.exception("%s: %s" % (str(e), str(v)))
