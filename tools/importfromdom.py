#!/usr/bin/python

# Python includes
import csv, grp, os, pwd, sys, urllib

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

def saveFile(row):
	(title, fileurl, postdate, theme, genre, artist, broadcastFlag) = (str(row['Title']), str(row['Audio File']), str(row['Post date']), str(row['Theme']), str(row['Genre']), str(row['Production Company / Band']), str(row['Authorized for Broadcast']))

	# Set the URL-decoded filename
	fileName = fileurl.split('/')[-1]
	fileName = urllib.unquote(fileName).decode('utf8')
	fileName = os.path.normpath(fileName)

	# Determine correct target path based on broadcastFlag
	path = ""
	if broadcastFlag == 'Yes':
		path = envproperties.UPLOAD_LIBRARY_FOLDER + "/" + fileName
	else:
		path = envproperties.UPLOAD_STAGING_FOLDER + "/" + fileName

	# Download the file if not already exists (will appear in current dir)
	if not os.path.exists(path):
		downloadFile(fileurl, fileName)

		# Move it to the correct target directory & set owner
		os.rename(fileName, path)
		os.chown(path, uid, gid)

	# Now save the song's metadata too
	saveMetadata(path, row)

	# TODO - check the other staging/library path and remove the file if it exists there
	# (To handle the flag getting checked and unchecked on the DOM side.)
	# (Also handle deleting from RadioDJ DB.)

	# TODO - if broadcastFlag is Yes, then insert into RadiDJ DB
	if broadcastFlag == 'Yes':
		writeToDB(path, row)

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

	jsonStr = JsonTools.ObjToJson(fields)

	# Assuming we have all required fields, write the metadata to the filesystem & set owner
	# This will overwrite file every time to pick up changes; which we want
	# TODO - how to get updates to RadioDJ DB?
	abs_path = filePath + ".metadata"
	metadata_file = open(abs_path, 'w')
	metadata_file.write(str(jsonStr))
	metadata_file.close()

	os.chown(abs_path, uid, gid)

def writeToDB(path, row):
	radioDj = DenhacRadioDjDb()
	radioDj.connect()

	# TODO - need to write an upsert SP in the DB, then CALL it here.
	# Let the DB handle the logic if-exists-then-update-else-insert

# Right now just show we can connect and select schema without error
	print radioDj._connect






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
#		printRow(row)
		saveFile(row)
