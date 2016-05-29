#!/usr/bin/python
import json, os, urllib, urllib2

######################################################################################
#           Helper Functions
######################################################################################

def shellquote(s):
	return "'" + s.replace("'", "'\\''") + "'"

def processRecord(record):
	# Get metadata for our specific record
	url = "https://archive.org/metadata/" + record['identifier']
#	print "Metadata url:", url
	response    = urllib2.urlopen(url)
	responseStr = response.read()
	data        = json.loads(responseStr)

	filename    = ''

	print "Processing ID: " + record['identifier']

	# Look for an HD file, by using frame size (which may or may not exist)
	for fileRow in data['files']:
		if "height" in fileRow and "width" in fileRow and fileRow['height'] == "1080" and fileRow['width'] == "1920":
			if fileRow['format'] == "QuickTime":
				filename = fileRow['name']:
				break
			elif fileRow['format'] == "h.264":
				filename = fileRow['name']
				break

	if not filename:
		print "No HD file found; skipping..."
		return

	savefileName = filename
	if filename.startswith('dom-'):
		savefileName = filename[4:]

	print "savefileName: ", savefileName

	# Download file. Thank you https://blog.archive.org/2011/03/31/how-archive-org-items-are-structured/4
	url = "http://archive.org/download/" + record['identifier'] + "/" + filename
#	print "Download url:", url

	videoFile     = "/mnt/ARCHIVE/cablecastHD/" + savefileName

	# Download file if not already exists
	if not os.path.exists(videoFile):
		print 'Downloading...',
		urllib.urlretrieve(url, videoFile)
		print 'done.'

######################################################################################
#           Main Script
######################################################################################

# Call archive.org to get the list of files in the library.
print "Calling archive.org..."
# Retrieves the entire DOM collection
url = "https://archive.org/advancedsearch.php?q=collection%3A%28denveropenmedia%29&fl%5B%5D=avg_rating&fl%5B%5D=btih&fl%5B%5D=call_number&fl%5B%5D=collection&fl%5B%5D=contributor&fl%5B%5D=coverage&fl%5B%5D=creator&fl%5B%5D=date&fl%5B%5D=description&fl%5B%5D=downloads&fl%5B%5D=external-identifier&fl%5B%5D=foldoutcount&fl%5B%5D=format&fl%5B%5D=headerImage&fl%5B%5D=identifier&fl%5B%5D=imagecount&fl%5B%5D=language&fl%5B%5D=licenseurl&fl%5B%5D=mediatype&fl%5B%5D=members&fl%5B%5D=month&fl%5B%5D=num_reviews&fl%5B%5D=oai_updatedate&fl%5B%5D=publicdate&fl%5B%5D=publisher&fl%5B%5D=related-external-id&fl%5B%5D=reviewdate&fl%5B%5D=rights&fl%5B%5D=scanningcentre&fl%5B%5D=source&fl%5B%5D=stripped_tags&fl%5B%5D=subject&fl%5B%5D=title&fl%5B%5D=type&fl%5B%5D=volume&fl%5B%5D=week&fl%5B%5D=year&sort%5B%5D=&sort%5B%5D=&sort%5B%5D=&rows=9999&page=1&output=json&callback=callback&save=yes#raw"
responseObj = urllib2.urlopen(url)
responseStr = responseObj.read()
responseStr = responseStr[9:-1]	# Cutting off the "callback()" part of the response
#print "Response:", responseStr

data = json.loads(responseStr)
data = data['response']

numFound = data['numFound']
print "Total Records:", numFound

allRecords = data['docs']

temptotal = 0
for record in allRecords:
	processRecord(record)

print "Done!"