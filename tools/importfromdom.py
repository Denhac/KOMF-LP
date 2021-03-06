#!/usr/bin/python
# -*- coding: utf-8 -*-

# Python includes
import csv
import os
import sys
import time

# Our own package includes
# insert() makes our path the first searched entry, as opposed to append()
sys.path.insert(0, '/var/www/api')
from komfpackage import envproperties, DenhacRadioDjDb, DenhacPidfile, RadioSongLib


######################################################################################
#           Global Objects
######################################################################################

# Library of all our helper functions needed for this script (manipulating id3s, setting metadata, etc)
songLib   = RadioSongLib()
appLogger = songLib.setAppLogger()
radioDjDb = DenhacRadioDjDb()

######################################################################################
# Be certain that only one copy of this script can run at a time
try:
    DenhacPidfile.createPidFile()
except:
    exType, value, traceback = sys.exc_info()
    appLogger.error(str(value))

#    DenhacEmail.SendEmail(fromAddr=envproperties.ERROR_FROM_EMAIL,
#                          toAddr=envproperties.ERROR_TO_EMAIL_LIST,
#                          subject='DOM Import Script Failed',
#                          body='Type:  ' + str(exType) + '\n' +
#                               'Value: ' + str(value) + '\n' +
#                               'Trace: ' + str(traceback))
    exit(0)

######################################################################################
#           Primary helper function - this is called row by row to process songs and outros
######################################################################################
def processRow(row):
    # Set our metadata dict from the csv row data
    metadata = songLib.getMetadataFromCsvRow(row)

    # Check if Broadcast flag has changed since we last saw this song, and move files if needed
    songLib.moveFilesIfBroadcastFlagChanged(metadata)

    # Download song if we don't already have it; move it to the right directory (staging or library)
    songLib.downloadSong(metadata)

    # If the csv specified an outro file, download it; otherwise generate one.
    songLib.downloadOrGenerateOutro(metadata)

    # Update metadata from the mp3's ID3 tag
    metadata = songLib.updateMetadataFromId3(metadata)

    # Save the metadata associated with the file to the filesystem
    songLib.saveMetadataToFile(metadata)

    # Insert/update, or remove from the RadioDJ DB, depending on broadcast flag
    songLib.handleBroadcastFlag(metadata)


def log_and_send_error(subject):
    e, v, t = sys.exc_info()
    appLogger.exception("%s: %s:%s" % (subject, str(e), str(v)))
#    msg_body = 'Type:  ' + str(e) + '\n' + 'Value: ' + str(v) + '\n'
#    DenhacEmail.SendEmail(fromAddr=envproperties.ERROR_FROM_EMAIL,
#                          toAddr=envproperties.ERROR_TO_EMAIL_LIST,
#                          subject=subject,
#                          body=msg_body)

######################################################################################
#           Main Script starts execution here
######################################################################################
appLogger.debug("==============================================")
appLogger.debug("Starting up, PID: " + str(DenhacPidfile.pid))

try:
    # Save a copy of the csv from DOM.  (This contains all files of Type=Audio submitted by DOM members.)
    fileName = RadioSongLib.downloadFile(envproperties.URL_FOR_DOM_FILELIST)

    # Open the file, get the data, and preprocess it.  Save data to our new file after we're done
    fi = open(fileName, 'rb')
    data = fi.read()
    fi.close()

    # Check for specific type of error, then retry immediately
    if data.startswith('The application did not respond in time.'):
        appLogger.info("Failed to retrieve audio_csv due to 'did not respond in time' error.  Retrying in 30 seconds.")
        time.sleep(30)
        fileName = RadioSongLib.downloadFile(envproperties.URL_FOR_DOM_FILELIST)
        fi = open(fileName, 'rb')
        data = fi.read()
        fi.close()

    # Attempt to remove NULL byte errors, umlauts, and accented e's
    fo = open(fileName+'converted.csv', 'wb')
    fo.write(data.replace('\x00', '').replace('ë', 'e').replace('é', 'e'))    # TODO and rows with just a '0' in them and nothing else...
    fo.close()
    fileName = fileName+'converted.csv'

    # Apr 2020 - if too small, just fail.
    # (Sometimes it reports success, but with a message like, "app did not respond in time".)
    filesize = os.path.getsize(fileName)
    if filesize < 1024 * 500:       # 500 KB
        raise RuntimeError("%s is too small for processing (%s).  Fail." % (fileName, filesize))

    # Clear the song failure table before starting the import loop
    radioDjDb.deleteSongImportFailures()

    # Read it in, parsing it as a csv
    with open(fileName, "rb") as audiofile:
        memreader = csv.DictReader(audiofile, delimiter=',')

        # Each row is a file to be downloaded, along with a few columns of metadata
        for row in memreader:
            try:
                processRow(row)
                songLib.totalRows += 1

            # If one row fails, just skip past this single row and continue in the loop
            except:
                e, v, t = sys.exc_info()
                radioDjDb.setSongImportFailure(row['Title'], row['Link'], str(e), str(v), str(t))
                appLogger.exception("%s:%s" % (str(e), str(v)))
                continue

        # Print out the song count when we're done
        songLib.printCounts()

    # Record our last successful import time for display on the tools page
    radioDjDb.setLastImportDatetime()

    # Run any ongoing/periodic maintenance that we need to do
    songLib.constantMaintenance()

    # Record our last successful maintenance time for display on the tools page
    radioDjDb.setLastMaintenanceDatetime()

    # Clean up, shut down and exit
    DenhacPidfile.removePidFile()
    appLogger.debug("Complete.")

except KeyboardInterrupt:
    # Just log and exit
    appLogger.exception("Keyboard interrupt; exiting.")
    DenhacPidfile.removePidFile()
    exit(0)

except:
    DenhacPidfile.removePidFile()
    log_and_send_error('DOM Import Script Failed')
