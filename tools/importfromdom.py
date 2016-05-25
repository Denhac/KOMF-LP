#!/usr/bin/python

# Python includes
import csv, datetime, grp, os, pwd, subprocess, sys, urllib

# Flask and other third-party includes
# TODO - Add logging to this program at some point...

#from logging.handlers import RotatingFileHandler
#from flask import Flask, request, session, render_template, redirect, url_for, abort, send_from_directory, jsonify
#from werkzeug import secure_filename

# Our own includes go here
# insert() makes our path the first searched entry, as opposed to append()
sys.path.insert(0, '/var/www/api/komfpackage')
import envproperties
from DenhacJsonLib import JsonTools
from DenhacDbLib import DenhacDb, DenhacRadioDjDb

######################################################################################
#           Helper Functions
######################################################################################
# Pull UID and GUID globally since they are used in multiple helper functions
uid = pwd.getpwnam(envproperties.APACHE_USER_NAME).pw_uid
gid = grp.getgrnam(envproperties.APACHE_GROUP_NAME).gr_gid

# Now is used in multiple places, so declare here
now = datetime.datetime.now()

# Use one DB connection the whole run
radioDj = DenhacRadioDjDb()

def downloadFile(location, targetName = None):
	if targetName is None:
		targetName = location.split('/')[-1]

	# Save the URL-decoded filename
	targetName = urllib.unquote(targetName).decode('utf8')
	targetName = os.path.normpath(targetName)

	urllib.urlretrieve(location, targetName)
	return targetName

def printRow(row):
	(title, fileurl, postdate, theme, genre, artist, broadcastFlag) = (str(row['Title']), str(row['Audio File']), str(row['Post date']), str(row['Theme']), str(row['Genre']), str(row['Production Company / Band']), str(row['Authorized for Broadcast']))

	print '==============================='
	print 'Title: ' + title
	print 'Audio File: ' + fileurl
	print 'Post date: ' + postdate
	print 'Theme: ' + theme
	print 'Genre: ' + genre
	print 'Production Company / Band: ' + artist
	print 'Authorized for Broadcast: ' + broadcastFlag

def getLibraryPath(fileName):
	return envproperties.UPLOAD_LIBRARY_FOLDER + "/" + fileName

def getStagingPath(fileName):
	return envproperties.UPLOAD_STAGING_FOLDER + "/" + fileName

def saveFile(row):
	(title, fileurl, postdate, theme, genre, artist, broadcastFlag) = (str(row['Title']), str(row['Audio File']), str(row['Post date']), str(row['Theme']), str(row['Genre']), str(row['Production Company / Band']), str(row['Authorized for Broadcast']))

	# Set the URL-decoded filename
	fileName = fileurl.split('/')[-1]
	fileName = urllib.unquote(fileName).decode('utf8')
	fileName = os.path.normpath(fileName)

	stagingPath = getStagingPath(fileName)
	libraryPath = getLibraryPath(fileName)

	# Check here in case Broadcast Flag has flipped back and forth since last time we saw the file:
	if broadcastFlag == 'Yes':
		# If file is still in staging, move it to the library.
		# Also move the metadata, but trust later code to regenerate it anyway.
		if os.path.exists(stagingPath):
			os.rename(stagingPath,               libraryPath)
		if os.path.exists(stagingPath + '.metadata'):
			os.rename(stagingPath + '.metadata', libraryPath + '.metadata')
	else:
		# If file is in the library, with Broadcast flag No, then it got dis-approved for some reason.  Move it back to staging.
		# Also move the metadata, but trust later code to regenerate it anyway.
		if os.path.exists(libraryPath):
			os.rename(libraryPath,               stagingPath)
			# Also need to handle deleting from RadioDJ DB here. Since we moved the file back to staging, it will fail to play, but let's be nice and get it out of the DJ list.
			radioDjDb.deleteSong(libraryPath)

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

	# Now save the song's metadata too
	metadata = dict()
	metadata = saveMetadata(targetPath, row)

	# If broadcastFlag is Yes, then insert into RadiDJ DB
	if broadcastFlag == 'Yes':
		writeToDB(targetPath, metadata)

def shellquote(s):
	return "'" + s.replace("'", "'\\''") + "'"

# yum install yasm gcc git
# git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg
# cd ffmpeg
# ./configure
# make && make install
def getDurationFromFile(filePath):
	cmd = "/usr/local/bin/ffprobe -i " + shellquote(filePath) + " -show_entries format=duration -v quiet -of csv=\"p=0\""
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	duration = proc.stdout.read()
	return duration[:-4]	# Reduce from 7 decimal places to 3

def saveMetadata(filePath, row):
	# Create metadata in JSON format
	fields = dict()
	fields['title']         = str(row['Title'])
	fields['postdate']      = str(row['Post date'])
	fields['theme']         = str(row['Theme'])
	fields['genre']         = str(row['Genre'])
	fields['artist']        = str(row['Production Company / Band'])
	fields['broadcastFlag'] = str(row['Authorized for Broadcast'])
	fields['fileurl']       = str(row['Audio File'])
	# We don't really need fileURL; need to save local file path instead
	fields['filepath']      = filePath
	# Set year to the current year at the time of import
	fields['year']          = now.year
	# Calculate duration in seconds and set in metadata
	fields['duration']      = getDurationFromFile(filePath)

	jsonStr = JsonTools.ObjToJson(fields)

	# Assuming we have all required fields, write the metadata to the filesystem & set owner
	# This will overwrite file every time to pick up changes; which we want
	abs_path = filePath + ".metadata"
	metadata_file = open(abs_path, 'w')
	metadata_file.write(str(jsonStr))
	metadata_file.close()

	os.chown(abs_path, uid, gid)
	return fields

def writeToDB(path, fields):
	genre_id = radioDj.getGenreIdByName(fields['genre'])

	radioDj.upsertSongs(path,
						song_type = 0,	# TODO - determine song_type from genre or other metadata
						id_genre  = genre_id,
						duration  = fields['duration'],
						artist    = fields['artist'],
						album     = "Unknown Album",
						year      = fields['year'],
						copyright = "Unknown Copyright",
						title     = fields['title'],
						publisher = "Unknown Publisher",
						composer  = "Unknown Composer")

######################################################################################
#           Main Script
######################################################################################

# Save a copy of the csv from DOM.  (This contains all song files submitted by DOM members.)
fileName = downloadFile(envproperties.URL_FOR_DOM_FILELIST)

# Read it in, parsing it as a csv
with open(fileName, "rb") as audiofile:
	memreader = csv.DictReader(audiofile, delimiter=',', quotechar='"')

	# Each row is a file to be downloaded, along with a few columns of metadata
	for row in memreader:
		saveFile(row)

print "Done!"