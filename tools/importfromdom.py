#!/usr/bin/python

# Python includes
import csv, datetime, grp, logging, os, pwd, subprocess, sys, threading, urllib
from logging.handlers import RotatingFileHandler

# Our own includes go here
# insert() makes our path the first searched entry, as opposed to append()
sys.path.insert(0, '/var/www/api/komfpackage')
import envproperties
from DenhacJsonLib import JsonTools
from DenhacDbLib import DenhacDb, DenhacRadioDjDb

# Third-party includes
import eyed3

######################################################################################
#           Global Construction / Configuration
######################################################################################
# Save our PID for later use
pid = os.getpid()
pidfile = '/tmp/importfromdom.pid'

# TODO - generalize this to a new DenhacLogger class in the next refactoring
#appLogger = logging.getLogger('PID:' + str(pid))
appLogger = logging.getLogger('ImportLogger')
appLogger.propagate = False

# TODO - revert to INFO once we're stable
#appLogger.setLevel(logging.INFO)
appLogger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

handler = RotatingFileHandler(envproperties.IMPORT_LOG_FILE, maxBytes=1024 * 1024 * 10, backupCount=20)
handler.setFormatter(formatter)

appLogger.addHandler(handler)
appLogger.debug("Starting up.")

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

def saveFile(row):
	global totalNewFiles, filesMovedToLibrary, filesMovedToStaging, radioDj, uid, gid

	# Transform from csv columns to local vars
	(title, fileurl, postdate, theme, genre, broadcastFlag,  indecencyFlag, outroUrl) = (str(row['Title']), str(row['Audio File']), str(row['Post date']), str(row['Theme']), str(row['Genre']), str(row['Authorized for Broadcast']), str(row['Indecent Content']), str(row['DJ Outro']))
	# Handle silly exception for a column that keeps changing back and forth in the export without warning....
	artist = ''
	if 'Production Company / Band' in row:
		artist = str(row['Production Company / Band'])
	if 'Artist/Production Company/Band' in row:
		artist = str(row['Artist/Production Company/Band'])

	# Set the URL-decoded filename
	fileName = fileurl.split('/')[-1]
	fileName = urllib.unquote(fileName).decode('utf8')
	fileName = os.path.normpath(fileName)

	stagingPath  = getStagingPath(fileName)
	libraryPath  = getLibraryPath(fileName)
	frontendPath = getFrontendPath(fileName)

	# Check here in case Broadcast Flag has flipped back and forth since last time we saw the file:
	if broadcastFlag == 'Yes':
		# If file is still in staging, move it to the library.
		# Also move the metadata, but trust later code to regenerate it anyway.
		if os.path.exists(stagingPath):
			os.rename(stagingPath,               libraryPath)
			filesMovedToLibrary += 1
		if os.path.exists(stagingPath + '.metadata'):
			os.rename(stagingPath + '.metadata', libraryPath + '.metadata')
	else:
		# If file is in the library, with Broadcast flag No, then it got dis-approved for some reason.  Move it back to staging.
		# Also move the metadata, but trust later code to regenerate it anyway.
		if os.path.exists(libraryPath):
			os.rename(libraryPath,               stagingPath)
			filesMovedToStaging += 1
			# Remove from RadioDJ DB. Since we moved the file back to staging, it will fail to play, but let's be nice and get it out of the DJ list.
			radioDj.deleteSong(frontendPath)

		if os.path.exists(libraryPath + '.metadata'):
			os.rename(libraryPath + '.metadata', stagingPath + '.metadata')

	# Determine correct target path based on broadcast Flag
	targetPath = stagingPath
	if broadcastFlag == 'Yes':
		targetPath = libraryPath

	# Download the file if not already exists:
	# (It will appear in current dir, then we have to move it.)
	if not os.path.exists(targetPath):
		# Download it, move it to the target directory, & set owner
		downloadFile(fileurl, fileName)
		os.rename(fileName, targetPath)
		os.chown(targetPath, uid, gid)
		totalNewFiles += 1

	# Download the outro file if not already exists
	if outroUrl:
		outroFile = outroUrl.rsplit('/', 1)[-1]
		outroFile = urllib.unquote(outroFile).decode('utf8')
		outroFile = os.path.normpath(outroFile)

		outroPath = targetPath.rsplit('/', 1)[0] + '/' + outroFile

		if not os.path.exists(outroPath):
			downloadFile(outroUrl, outroFile)
			os.rename(outroFile, outroPath)
			os.chown(outroPath, uid, gid)
			totalNewFiles += 1

	# Add frontendpath to row to carry it through to metadata
	row['frontendPath'] = frontendPath

	# Now save the song's metadata too
	metadata = dict()
	metadata = saveMetadata(targetPath, row)

	# If broadcastFlag is Yes, then insert into RadioDJ DB
	if broadcastFlag == 'Yes':
		writeToDB(frontendPath, metadata)

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

def saveMetadata(filePath, row):
	global uid, gid, radioDj

	# Create metadata in JSON format
	fields = dict()
	# Fields directly from the csv
	fields['title']         = str(row['Title'])
	fields['postdate']      = str(row['Post date'])
	fields['theme']         = str(row['Theme'])
	fields['genre']         = str(row['Genre'])
	# Handle silly exception for a column that keeps changing back and forth in the export without warning....
	fields['artist']        = ''
	if 'Production Company / Band' in row:
		fields['artist']    = str(row['Production Company / Band'])
	if 'Artist/Production Company/Band' in row:
		fields['artist']    = str(row['Artist/Production Company/Band'])
	fields['album']         = str(row['Album/Project'])
	fields['broadcastFlag'] = str(row['Authorized for Broadcast'])
	fields['indecencyFlag'] = str(row['Indecent Content'])
	fields['fileurl']       = str(row['Audio File'])
	fields['outroFile']     = str(row['DJ Outro'])
	# We don't really need fileURL; need to save local file path instead
	fields['filepath']      = filePath
	fields['frontendPath']  = row['frontendPath']
	# Set year to the current year at the time of import
	fields['year']          = now.year
	# Calculate duration in seconds and set in metadata
	fields['duration']      = getDurationFromFile(filePath)
	# RadioDJ really likes having these tags... dunno why it can't calculate it itself from the duration, but whatever.
#	fields['cue_times']     = "&sta=0&xta=" + str(float(fields['duration']) - float(envproperties.FADE_OUT_SEC))+ "&end=" + fields['duration'] + "&fin=" + str(envproperties.FADE_IN_SEC) + "&fou=" + str(envproperties.FADE_OUT_SEC)
	fields['cue_times']     = getCueTimesFromDuration(fields['duration'] )

	# Unknown fields at this time but required by RadioDJ DB
	fields['copyright'] = "Unknown Copyright"
	fields['publisher'] = "Unknown Publisher"
	fields['composer']  = "Unknown Composer"

	# For each of the following fields: artist, album, genre:
	# 	If DOM is missing value, but mp3 ID3 has it, use ID3 tag
	# 	If DOm value exists but mp3 ID3 tag does not have it, save to ID3 tag
	# 	else Unknown

	eyed3.log.setLevel("ERROR")
	audiofile = eyed3.load(filePath)
	tag = audiofile.tag
	writeTag = False

	#############################  artist  ################################
	# IF DOM is missing the value, but ID3 has it, save to our metadata
	if not fields['artist'] and tag is not None and tag.artist is not None:
		fields['artist'] = tag.artist

	# IF DOM value exists and ID3 tag does not, save to ID3
	if fields['artist'] and tag is not None and tag.artist is None:
		tag.artist = fields['artist'].decode('unicode-escape')
		writeTag = True

	# IF they were both missing, set to Unknown
	if not fields['artist'] and (tag is None or tag.artist is None):
		fields['artist'] = 'Unknown Artist'


	#############################  album  #################################
	# IF DOM is missing the value, but ID3 has it, save to our metadata
	if not fields['album'] and tag is not None and tag.album is not None:
		fields['album'] = tag.album

	# IF DOM value exists and ID3 tag does not, save to ID3
	if fields['album'] and tag is not None and tag.album is None:
		tag.album = fields['album'].decode('unicode-escape')
		writeTag = True

	# IF they were both missing, set to Unknown
	if not fields['album'] and (tag is None or tag.album is None):
		fields['album'] = 'Unknown Album'


	#############################  genre  #################################
	genre_id  = radioDj.getGenreIdByName(fields['genre'])
	# IF DOM is missing the value, but ID3 has it, save to our metadata
	if genre_id == 60 and tag is not None and tag.genre is not None:
		fields['genre'] = tag.genre.name

	# IF DOM value exists and ID3 tag does not, save to ID3
	if fields['genre'] and tag is not None and tag.genre is None:
		tag.genre = fields['genre'].decode('unicode-escape')
		writeTag = True

	if writeTag and tag is not None:
		try:
			tag.save()
			appLogger.debug("Saved new ID3 tag:" + filePath)
		except NotImplementedError:		# eyed3 fails to write ID3 v2.2 tags
			pass

	jsonStr = JsonTools.ObjToJson(fields)

	# Assuming we have all required fields, write the metadata to the filesystem & set owner
	# This will overwrite file every time to pick up changes; which we want
	abs_path = filePath + ".metadata"
	metadata_file = open(abs_path, 'w')
	metadata_file.write(str(jsonStr))
	metadata_file.close()

	os.chown(abs_path, uid, gid)
	return fields


def getFilenameFromUrl(url):
	fileName = url.rsplit('/', 1)[-1]
	fileName = urllib.unquote(fileName).decode('utf8')
	fileName = os.path.normpath(fileName)
	return fileName

def writeToDB(path, fields):
	global radioDj

	genre_id  = radioDj.getGenreIdByName(fields['genre'])
	subcat_id = radioDj.getSubcategoryIdByName(fields['theme'])

	# Set certain defaults that may be changed if we have an Indecent file
	enabled      = 1
	comments     = ''
	title        = fields['title']
	play_limit   = 0
	limit_action = 0

	if fields['indecencyFlag'] == "Yes":
		enabled      = 0
		comments     = "Importing with enabled = OFF due to Indecent content.  Change flag manually to schedule."
		title       += " - EXPLICIT"
		play_limit   = 1
		limit_action = 1

	radioDj.upsertSongs(path,
						song_type    = 0,			# Regular songs are 0 (See Dave's email)
						id_subcat    = subcat_id,
						id_genre     = genre_id,
						duration     = fields['duration'],
						artist       = fields['artist'],
						album        = fields['album'],
						year         = fields['year'],
						copyright    = fields['copyright'],
						title        = title,
						publisher    = fields['publisher'],
						composer     = fields['composer'],
						cue_times    = fields['cue_times'],
						enabled      = enabled,
						comments     = comments,
						play_limit   = play_limit,
						limit_action = limit_action)

	# IF an outro file exists, insert it too
	if fields['outroFile']:
		outroFilename = getFilenameFromUrl(fields['outroFile'])
		outroPath = getFrontendPath(outroFilename)
		duration = getDurationFromFile(getLibraryPath(outroFilename))

		radioDj.upsertSongs(outroPath,
							song_type    = 2,		# Outros should be type 2.
							id_subcat    = 19,		# 19 for Sweeper / Outro
							id_genre     = genre_id,
							duration     = duration,
							artist       = fields['artist'],
							album        = fields['album'],
							year         = fields['year'],
							copyright    = fields['copyright'],
							title        = title + ' - OUTRO',
							publisher    = fields['publisher'],
							composer     = fields['composer'],
#							cue_times    = # don't use cue times; they would be for the main file anyway
							# Actually... restoring cue times; RadioDJ needs them for proper schedule predicting
							cue_times    = getCueTimesFromDuration(duration),
							enabled      = enabled,
							comments     = comments,
							play_limit   = play_limit,
							limit_action = limit_action)

def constantMaintenance():
	# Update any P:\ paths to \\<address> network path instead (fixes issues caused by manual uploads as opposed to automated imports)
	radioDj.autoUpdatePath()

	# Call the URL to ask RadioDJ to refresh its Events list (so that other users with separate RadioDJ front ends can create schedules.  This triggers the master RadioDJ instance to refresh them.)
	response = urllib.urlopen("http://192.168.22.16:8080/opt?auth=104.7lpfm&command=RefreshEvents")
	responseText = response.read()
	appLogger.debug("Refresh events response: " + responseText)

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
			saveFile(row)
			totalRows += 1

	if totalRows > 0:
		appLogger.debug("Total rows analyzed: " + str(totalRows))
	if totalNewFiles > 0:
		appLogger.info("Total new files downloaded: " + str(totalNewFiles))
	if filesMovedToLibrary > 0:
		appLogger.info("Total files approved and moved to library: " + str(filesMovedToLibrary))
	if filesMovedToStaging > 0:
		appLogger.info("Total files un-approved and moved back to staging: " + str(filesMovedToStaging))

	# Run any ongoing DB maintenance that we need to do
	constantMaintenance()


	appLogger.debug("Complete.")

finally:
	removePidFile()