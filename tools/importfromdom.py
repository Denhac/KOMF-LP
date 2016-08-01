#!/usr/bin/python

# Python includes
import csv, datetime, grp, logging, os, pwd, subprocess, sys, threading, urllib
from logging.handlers import RotatingFileHandler

# Our own package includes
# insert() makes our path the first searched entry, as opposed to append()
sys.path.insert(0, '/var/www/api/komfpackage')
import envproperties
from DenhacJsonLib import JsonTools
from DenhacDbLib import DenhacDb, DenhacRadioDjDb
from DenhacTTSLib import TTSTools

# Third-party includes
import eyed3

######################################################################################
#           Global Construction / Configuration
######################################################################################
# Save our PID for later use
pid = os.getpid()
pidfile = '/tmp/importfromdom.pid'

# TODO - generalize this to a new DenhacLogger class in the next refactoring
appLogger = logging.getLogger('ImportLogger')
appLogger.propagate = False

# TODO - revert to INFO once we're stable
#appLogger.setLevel(logging.INFO)
appLogger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

handler = RotatingFileHandler(envproperties.IMPORT_LOG_FILE, maxBytes=1024 * 1024 * 10, backupCount=20)
handler.setFormatter(formatter)

appLogger.addHandler(handler)
appLogger.debug("Starting up, PID: " + str(pid))

# Pull UID and GUID globally since they are used in multiple helper functions
uid = pwd.getpwnam(envproperties.APACHE_USER_NAME).pw_uid
gid = grp.getgrnam(envproperties.APACHE_GROUP_NAME).gr_gid

# Now is used in multiple places, so declare here
now = datetime.datetime.now()

# Use one DB connection the whole run
radioDj = DenhacRadioDjDb()

# Track total # of files downloaded/moved; log at the end
totalRows           = 0
totalNewFiles       = 0
filesMovedToLibrary = 0
filesMovedToStaging = 0

######################################################################################
#           Helper Functions
######################################################################################
def is_pid_running(pid):
	""" Check For the existence of a unix pid. """
	try:
		os.kill(pid, 0)		# Sig 0 is "are you there, process? What's your status?"
	except OSError:
		return False
	else:
		return True

def createPidFile():
	global pid, pidfile

	if os.path.isfile(pidfile):
		pidFromFile = int(open(pidfile).read())

		if is_pid_running(pidFromFile):
			appLogger.error("Another instance of this script is running under PID %s.  Exiting.", str(pidFromFile))
			exit(0)

	# Write out our own PID now if we're continuing
	open(pidfile, 'w').write(str(pid))

def removePidFile():
	global pidfile
	if os.path.isfile(pidfile):
		os.remove(pidfile)

def downloadFile(location, targetName = None):
	if targetName is None:
		targetName = location.split('/')[-1]

	# Save the URL-decoded filename
	targetName = urllib.unquote(targetName).decode('utf8')
	targetName = os.path.normpath(targetName)

	urllib.urlretrieve(location, targetName)
	return targetName

def getLibraryPath(fileName):
	return envproperties.UPLOAD_LIBRARY_FOLDER + "/" + fileName

def getStagingPath(fileName):
	return envproperties.UPLOAD_STAGING_FOLDER + "/" + fileName

def getFrontendPath(fileName):
	return envproperties.RADIODJ_CLIENT_FOLDER + "\\" + fileName


def shellquote(s):
	return "'" + s.replace("'", "'\\''") + "'"

# HUGE FRIGGING THANK YOU TO https://gist.github.com/icaliman/1ee56b7f3ed5abf0dec1
# (Installing ffmpeg and libmp3lame where they worked nicely together!)
# But with replacing this command:
# PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure \
#  --prefix="$HOME/ffmpeg_build" \
#  --extra-cflags="-I$HOME/ffmpeg_build/include" \
#  --extra-ldflags="-L$HOME/ffmpeg_build/lib" \
#  --bindir="$HOME/bin" \
#  --enable-libmp3lame
def getDurationFromFile(filePath):
	cmd = "/root/bin/ffprobe -i " + shellquote(filePath) + " -show_entries format=duration -v quiet -of csv=\"p=0\""
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	duration = proc.stdout.read()
	return duration[:-4]	# Reduce from 7 decimal places to 3

def getCueTimesFromDuration(duration):
	return "&sta=0&xta=" + str(float(duration) - float(envproperties.FADE_OUT_SEC)) + "&end=" + duration + "&fin=" + str(envproperties.FADE_IN_SEC) + "&fou=" + str(envproperties.FADE_OUT_SEC)

def getFilenameFromUrl(url):
	fileName = url.rsplit('/', 1)[-1]
	fileName = urllib.unquote(fileName).decode('utf8')
	fileName = os.path.normpath(fileName)
	return fileName

######################################################################################
#           Processing Functions (all called from the processRow() fn)
######################################################################################
def getMetadataFromCsvRow(row):
	metadata = dict()

	# No check on required fields; let them throw KeyError exception
	metadata['title'] = str(row['Title'])
	metadata['fileurl'] = str(row['Audio File'])
	metadata['theme'] = str(row['Theme'])
	metadata['genre'] = str(row['Genre'])
	metadata['broadcastFlag'] = str(row['Authorized for Broadcast'])
	metadata['indecencyFlag'] = str(row['Indecent Content'])

	# Handle silly exception for a column that keeps changing back and forth in the export without warning....
	metadata['artist'] = ''
	if 'Production Company / Band' in row:
		metadata['artist'] = str(row['Production Company / Band'])
	elif 'Artist/Production Company/Band' in row:
		metadata['artist'] = str(row['Artist/Production Company/Band'])
	else:
		raise KeyError("Artist column not found!")

	# Handle optional fields
	metadata['postdate'] = ''
	metadata['outroUrl'] = ''
	metadata['album']    = ''

	if 'Post date' in row:
		metadata['postdate'] = str(row['Post date'])
	if 'DJ Outro' in row:
		metadata['outroUrl'] = str(row['DJ Outro'])
	if 'Album/Project' in row:
		metadata['album']    = str(row['Album/Project'])

	# Set year to the current year at the time of import, TODO - until we can get this value from the csv
	metadata['year'] = now.year

	# Unknown fields at this time but required by RadioDJ DB - TODO, get these fields from the csv one day
	metadata['copyright'] = "Unknown Copyright"
	metadata['publisher'] = "Unknown Publisher"
	metadata['composer']  = "Unknown Composer"

	# Set the URL-decoded filename and various necessary paths
#	fileName = metadata['fileurl'].split('/')[-1]
#	fileName = urllib.unquote(fileName).decode('utf8')
#	fileName = os.path.normpath(fileName)
	fileName = getFilenameFromUrl(metadata['fileurl'])

	outroFileName = ''
	if metadata['outroUrl']:
		outroFileName = getFilenameFromUrl(metadata['outroUrl'])
	else:
		outroFileName = fileName[:-4] + ' - OUTRO.mp3'

	metadata['fileName']       = fileName
	metadata['outroFileName']  = outroFileName
	metadata['stagingPath']    = getStagingPath(fileName)
	metadata['libraryPath']    = getLibraryPath(fileName)
	metadata['frontendPath']   = getFrontendPath(fileName)

	metadata['targetPath']        = metadata['stagingPath']
	metadata['outroPath']         = getStagingPath(metadata['outroFileName'])
	metadata['outroFrontendPath'] = getFrontendPath(metadata['outroFileName'])
	if metadata['broadcastFlag']  == 'Yes':
		metadata['targetPath']    = metadata['libraryPath']
		metadata['outroPath']     = getLibraryPath(metadata['outroFileName'])

	return metadata

def moveFilesIfBroadcastFlagChanged(metadata):
	global filesMovedToLibrary, filesMovedToStaging

	# If song exists in library, and Broadcast = No, move it (and its metadata) back to staging
	if os.path.exists(metadata['libraryPath']) and metadata['broadcastFlag'] == 'No':
		appLogger.debug("Broadcast disabled; moving file to " + metadata['stagingPath'])

		os.rename(metadata['libraryPath'], metadata['stagingPath'])
		filesMovedToStaging += 1
		# Move metadata
		if os.path.exists(metadata['libraryPath'] + '.metadata'):
			os.rename(metadata['libraryPath'] + '.metadata', metadata['stagingPath'] + '.metadata')
		# Move outro
		if os.path.exists(getLibraryPath(metadata['outroFileName'])):
			os.rename(getLibraryPath(metadata['outroFileName']), getStagingPath(metadata['outroFileName']))

	# If song exists in staging, and Broadcast = Yes, move it (and its metadata) to the library
	elif os.path.exists(metadata['stagingPath']) and metadata['broadcastFlag'] == 'Yes':
		appLogger.debug("Broadcast enabled; moving file to " + metadata['libraryPath'])

		os.rename(metadata['stagingPath'], metadata['libraryPath'])
		filesMovedToLibrary += 1
		# Move metadata
		if os.path.exists(metadata['stagingPath'] + '.metadata'):
			os.rename(metadata['stagingPath'] + '.metadata', metadata['libraryPath'] + '.metadata')
		# Move outro
		if os.path.exists(getStagingPath(metadata['outroFileName'])):
			os.rename(getStagingPath(metadata['outroFileName']), getLibraryPath(metadata['outroFileName']))

def downloadSong(metadata):
	global totalNewFiles, uid, gid

	# If song exists in library, and broadcast = Yes, nothing to do
	if os.path.exists(metadata['libraryPath']) and metadata['broadcastFlag'] == 'Yes':
		return

	# If song exists in staging, and broadcast = No, nothing to do
	if os.path.exists(metadata['stagingPath']) and metadata['broadcastFlag'] == 'No':
		return

	# Otherwise, download the file to the correct target diretory, & set owner
	appLogger.debug("Downloading new file: " + metadata['targetPath'])
	downloadFile(metadata['fileurl'], metadata['targetPath'])
	os.chown(metadata['targetPath'], uid, gid)
	totalNewFiles += 1
	appLogger.debug("Download complete.")

def downloadOrGenerateOutro(metadata):
	global totalNewFiles, uid, gid

	# If an outro file already exists from a previous run, nothing to do
	if os.path.exists(metadata['outroPath']):
		return

	outroFile = ''
	# If an Outro is defined in the csv file, download and use that one
	if metadata['outroUrl']:
		outroFile = downloadFile(metadata['outroUrl'], metadata['outroFileName'])
		appLogger.debug("Outro downloaded: " + metadata['outroFileName'])

	# If there is no outro URL, then create an outro and move it to the correct location
	else:
		appLogger.debug("Generating Outro: " + metadata['outroFileName'])

		tts1 = None
		if metadata['artist']:
			tts1 = TTSTools(metadata['title'], metadata['artist'])
		else:
			tts1 = TTSTools(metadata['title'])

		outroFile = tts1.construct_tts_file()
		appLogger.debug("Outro generated.")

	# Move it to the correct target directory, set correct permissions and track the count
	os.rename(outroFile, metadata['outroPath'])
	os.chown(metadata['outroPath'], uid, gid)
	totalNewFiles += 1

def updateMetadataFromId3(metadata):
	global radioDj

	# Calculate duration in seconds and set in metadata
	metadata['duration']        = getDurationFromFile(metadata['targetPath'])
	metadata['outro_duration']  = getDurationFromFile(metadata['outroPath'])

	# RadioDJ really likes having cue_times... dunno why it can't calculate it itself from the duration (like it does during a manual import), but whatever.
	metadata['cue_times']       = getCueTimesFromDuration(metadata['duration'] )
	metadata['outro_cue_times'] = getCueTimesFromDuration(metadata['outro_duration'] )

	# For each of the following fields: artist, album, genre:
	# 	If DOM is missing value, but mp3 ID3 has it, use ID3 tag
	# 	If DOM value exists but mp3 ID3 tag does not have it, save DOM's value to ID3 tag
	# 	else set to Unknown

	eyed3.log.setLevel("ERROR")
	audiofile = eyed3.load(metadata['targetPath'])
	tag = audiofile.tag
	writeTag = False

	#############################  artist  ################################
	# IF DOM is missing the value, but ID3 has it, save to our metadata
	if not metadata['artist'] and tag is not None and tag.artist is not None:
		metadata['artist'] = tag.artist

	# IF DOM value exists and ID3 tag does not, save to ID3
	if metadata['artist'] and tag is not None and tag.artist is None:
		tag.artist = metadata['artist'].decode('unicode-escape')
		writeTag = True

	# IF they were both missing, set to Unknown
	if not metadata['artist'] and (tag is None or tag.artist is None):
		metadata['artist'] = 'Unknown Artist'

	#############################  album  #################################
	# IF DOM is missing the value, but ID3 has it, save to our metadata
	if not metadata['album'] and tag is not None and tag.album is not None:
		metadata['album'] = tag.album

	# IF DOM value exists and ID3 tag does not, save to ID3
	if metadata['album'] and tag is not None and tag.album is None:
		tag.album = metadata['album'].decode('unicode-escape')
		writeTag = True

	# IF they were both missing, set to Unknown
	if not metadata['album'] and (tag is None or tag.album is None):
		metadata['album'] = 'Unknown Album'

	#############################  genre  #################################
	genre_id  = radioDj.getGenreIdByName(metadata['genre'])
	# IF DOM is missing the value, but ID3 has it, save to our metadata
	if genre_id == 60 and tag is not None and tag.genre is not None:
		metadata['genre'] = tag.genre.name

	# IF DOM value exists and ID3 tag does not, save to ID3
	if metadata['genre'] and tag is not None and tag.genre is None:
		tag.genre = metadata['genre'].decode('unicode-escape')
		writeTag = True

	if writeTag and tag is not None:
		try:
			tag.save()
			appLogger.debug("Saved new ID3 tag: " + metadata['targetPath'])
		except NotImplementedError:		# eyed3 fails to write ID3 v2.2 tags; ignore
			pass

	return metadata

def saveMetadataToFile(metadata):
	global uid, gid

	# Write the metadata to the filesystem & set owner
	# This will overwrite file every time to pick up changes; which we want
	abs_path = metadata['targetPath'] + ".metadata"
	metadata_file = open(abs_path, 'w')

	jsonStr = JsonTools.ObjToJson(metadata)
	metadata_file.write(str(jsonStr))
	metadata_file.close()

	os.chown(abs_path, uid, gid)

def writeToDB(metadata):
	global radioDj

	genre_id  = radioDj.getGenreIdByName(metadata['genre'])
	subcat_id = radioDj.getSubcategoryIdByName(metadata['theme'])

	# Set certain defaults that may be changed if we have an Indecent file
	enabled      = 1
	comments     = ''
	title        = metadata['title']
	play_limit   = 0
	limit_action = 0

	if metadata['indecencyFlag'] == "Yes":
		enabled      = 0
		comments     = "Importing with enabled = OFF due to Indecent content.  Change flag manually to schedule."
		title       += " - EXPLICIT"
		play_limit   = 1
		limit_action = 1

	radioDj.upsertSongs(metadata['frontendPath'],
						song_type    = 0,			# Regular songs are 0 (See Dave's email)
						id_subcat    = subcat_id,
						id_genre     = genre_id,
						duration     = metadata['duration'],
						artist       = metadata['artist'],
						album        = metadata['album'],
						year         = metadata['year'],
						copyright    = metadata['copyright'],
						title        = title,
						publisher    = metadata['publisher'],
						composer     = metadata['composer'],
						cue_times    = metadata['cue_times'],
						enabled      = enabled,
						comments     = comments,
						play_limit   = play_limit,
						limit_action = limit_action)

	# Outro files always exist by this point now
	radioDj.upsertSongs(metadata['outroFrontendPath'],
						song_type    = 2,		# Outros should be type 2.
						id_subcat    = 19,		# 19 for Sweeper / Outro
						id_genre     = genre_id,
						duration     = metadata['outro_duration'],
						artist       = metadata['artist'],
						album        = metadata['album'],
						year         = metadata['year'],
						copyright    = metadata['copyright'],
						title        = title + ' - OUTRO',
						publisher    = metadata['publisher'],
						composer     = metadata['composer'],
						cue_times    = metadata['outro_cue_times'],
						enabled      = enabled,
						comments     = comments,
						play_limit   = play_limit,
						limit_action = limit_action)

def constantMaintenance():
	# Update any P:\ paths to \\<address> network path instead (fixes issues caused by manual uploads as opposed to automated imports)
	radioDj.autoUpdatePath()

	# Call the URL to ask RadioDJ to refresh its Events list (so that other users with separate RadioDJ front ends can create schedules.  This triggers the master RadioDJ instance to refresh them.)
	# TODO - move this URL to envprops
	response = urllib.urlopen("http://192.168.22.16:8080/opt?auth=104.7lpfm&command=RefreshEvents")
	responseText = response.read()
	appLogger.debug("Refresh events response: " + responseText)

######################################################################################
#           Primary helper function - is called row by row to process songs and outros
######################################################################################
def processRow(row):
	global radioDj

	# Set our metadata dict from the csv row data
	metadata = getMetadataFromCsvRow(row)

	# Check if Broadcast flag has changed since we last saw this song, and move files as needed
	moveFilesIfBroadcastFlagChanged(metadata)

	# Download song if we don't already have it; move it to the right directory (staging or library)
	downloadSong(metadata)

	# If the csv specified an outro file, download it; otherwise generate one.
	downloadOrGenerateOutro(metadata)

	# Update metadata from the mp3's ID3 tag
	metadata = updateMetadataFromId3(metadata)

	# Save the metadata associated with the file to the filesystem
	saveMetadataToFile(metadata)

	# If broadcastFlag is Yes, then insert into RadioDJ DB
	if metadata['broadcastFlag'] == 'Yes':
		writeToDB(metadata)
	# Otherwise remove the file and its outro from the DB
	else:
		radioDj.deleteSong(metadata['targetPath'])
		radioDj.deleteSong(metadata['outroPath'])

######################################################################################
#           Main Script
######################################################################################
try:
	createPidFile()

	# Save a copy of the csv from DOM.  (This contains all files of Type=Audio submitted by DOM members.)
	fileName = downloadFile(envproperties.URL_FOR_DOM_FILELIST)

	# Read it in, parsing it as a csv
	with open(fileName, "rb") as audiofile:
		memreader = csv.DictReader(audiofile, delimiter=',')

		# Each row is a file to be downloaded, along with a few columns of metadata
		for row in memreader:
			processRow(row)
			totalRows += 1


			# TODO - remove me
			if totalRows > 20:
				break





	if totalRows > 0:
		appLogger.debug("Total rows analyzed: " + str(totalRows))
	if totalNewFiles > 0:
		appLogger.info("Total new files downloaded/generated: " + str(totalNewFiles))
	if filesMovedToLibrary > 0:
		appLogger.info("Total files approved and moved to library: " + str(filesMovedToLibrary))
	if filesMovedToStaging > 0:
		appLogger.info("Total files un-approved and moved back to staging: " + str(filesMovedToStaging))






	# Run any ongoing DB maintenance that we need to do
# TODO - UNCOMMENT ME
#	constantMaintenance()







	appLogger.debug("Complete.")

finally:
	removePidFile()
