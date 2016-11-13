#!/usr/bin/python

# Python includes
import csv, sys

# Our own package includes
# insert() makes our path the first searched entry, as opposed to append()
sys.path.insert(0, '/var/www/api')
from komfpackage import envproperties, DenhacEmail, DenhacPidfile, RadioSongLib

######################################################################################
#           Global Objects
######################################################################################

# Library of all our helper functions needed for this script (manipulating id3s, setting metadata, etc)
songLib   = RadioSongLib()
appLogger = songLib.setAppLogger()

######################################################################################
# Be certain that only one copy of this script can run at a time
try:
	DenhacPidfile.createPidFile()
except:
	exType, value, traceback = sys.exc_info()
	appLogger.error(str(value))
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

######################################################################################
#           Main Script starts execution here
######################################################################################
appLogger.debug("==============================================")
appLogger.debug("Starting up, PID: " + str(DenhacPidfile.pid))

try:
	# Save a copy of the csv from DOM.  (This contains all files of Type=Audio submitted by DOM members.)
	fileName = RadioSongLib.downloadFile(envproperties.URL_FOR_DOM_FILELIST)

	# Read it in, parsing it as a csv
	with open(fileName, "rb") as audiofile:
		memreader = csv.DictReader(audiofile, delimiter=',')

		# Each row is a file to be downloaded, along with a few columns of metadata
		for row in memreader:
			processRow(row)
			songLib.totalRows += 1

		songLib.printCounts()

	# Run any ongoing/periodic maintenance that we need to do, then shut down and exit
	songLib.constantMaintenance()
	DenhacPidfile.removePidFile()
	appLogger.debug("Complete.")

except KeyboardInterrupt:
	# Just log and exit
	appLogger.exception("Keyboard interrupt; exiting.")
	DenhacPidfile.removePidFile()
	exit(0)

except:
	appLogger.exception("Exception caught; aborting.")
	DenhacPidfile.removePidFile()

	exType, value, traceback = sys.exc_info()
	DenhacEmail.SendEmail(fromAddr = 'autobot@denhac.org',
						  toAddr   = ['anthony.stonaker@gmail.com'],
						  subject  = 'DOM Import Script Failed',
						  body     = 'Type:  ' + str(exType) + '\n' +
						  			 'Value: ' + str(value) + '\n' +
						  			 'Trace: ' + str(traceback))