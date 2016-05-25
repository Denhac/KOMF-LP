#!/usr/bin/python

# Python includes
import json, os, subprocess, sys, urllib, urllib2


# Flask and other third-party includes
# TODO - Add logging to this program at some point...


# Our own includes go here
# insert() makes our path the first searched entry, as opposed to append()
sys.path.insert(0, '/var/www/api/komfpackage')
import envproperties

######################################################################################
#           Helper Functions
######################################################################################

def shellquote(s):
	return "'" + s.replace("'", "'\\''") + "'"

def processRecord(record):
	# Get metadata for our specific record
	url = "https://archive.org/metadata/" + record['identifier']
	print "Metadata url:", url
	response    = urllib2.urlopen(url)
	responseStr = response.read()
	data        = json.loads(responseStr)

	filename = ''
	for fileRow in data['files']:
		if fileRow['name'].endswith('.mp4') and not fileRow['name'].endswith('_512kb.mp4'):
			filename = fileRow['name']
			break

	print "Filename:", filename

	if not filename:
		print "No mp4 file found; skipping..."
		return

	# Download file. Thank you https://blog.archive.org/2011/03/31/how-archive-org-items-are-structured/
	url = "http://archive.org/download/" + record['identifier'] + "/" + filename
#	print "Download url:", url

	videoFile     = envproperties.TRANSCODE_FOLDER + "/" + filename
	transcodeFile = videoFile[:-4] + ".mp3"
	metadataFile  = transcodeFile  + ".metadata"

	# Download file if not already exists
	if not os.path.exists(videoFile):
		urllib.urlretrieve(url, envproperties.TRANSCODE_FOLDER + "/" + filename)

	# Transcode file to mp3, if not already exists
	if not os.path.exists(transcodeFile):
		# TODO - fix literal pathing; this breaks portability.
		# But if I just use 'ffmpeg', then the subshell doesn't have the same env vars, so command not found... doh
		cmd = "/usr/local/bin/ffmpeg -i " + shellquote(videoFile) + " -f wav - | lame - " + shellquote(transcodeFile)
		proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

	# Save the metadata (don't check exists; we want to overwrite and get latest data always)
	metadata_file = open(metadataFile, 'w')
	metadata_file.write(str(responseStr))
	metadata_file.close()

######################################################################################
#           Main Script
######################################################################################

# Call archive.org to get the list of files in the library.
#response = urllib2.urlopen(envproperties.ARCHIVE_ORG_QUERY_URL)
#print "Response: ", str(response.read())
#data = json.load(response)   
#print data
# TODD - For now, read from a file.  Switch back to URL as the last step.
with open('archive.org.query.response', 'r') as myfile:
    data=myfile.read()
#print "Response: ", data

newdata = data[9:-1]	# Cutting off the "callback()" part of the response
#print "New Data: ", newdata

obj = json.loads(newdata)    # obj now contains a dict of the data
#print "Obj: ", response

response = obj['response']
#print "Response: ", response

numFound = response['numFound']
print "Total Records:", numFound



allRecords = response['docs']


temptotal = 0
for record in allRecords:
	processRecord(record)

	# TODO - remove this when we're ready to run for the full set
	temptotal += 1
	if temptotal == 12:
		break







print "Done!"