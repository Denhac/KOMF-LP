#!/usr/bin/python

# Python includes
import json, os, subprocess, sys, urllib, urllib2
from werkzeug import secure_filename

# Our own includes go here
# insert() makes our path the first searched entry, as opposed to append()
sys.path.insert(0, '/var/www/api')
from komfpackage import envproperties, JsonTools

######################################################################################
#           Helper Functions
######################################################################################

def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"

def getDurationFromFile(filePath):
    cmd = "/root/bin/ffprobe -i " + shellquote(filePath) + " -show_entries format=duration -v quiet -of csv=\"p=0\""
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    duration = proc.stdout.read()
    return duration[:-4]    # Reduce from 7 decimal places to 3

def processRecord(record, folderName):
    # Get metadata for our specific record
    url = "https://archive.org/metadata/" + record['identifier']
#    print "Metadata url:", url
    response    = urllib2.urlopen(url)
    responseStr = response.read()
    data        = json.loads(responseStr)

    filename    = ''
    # Look for an mp4 file first to save bandwidth/time/space
    for fileRow in data['files']:
        if fileRow['name'].endswith('.mp4') and not fileRow['name'].endswith('_512kb.mp4'):
            filename = fileRow['name']
            break

    # Ok, fallback to the mpeg-2 that every entry is supposed to have by default.
    if not filename:
        for fileRow in data['files']:
            if fileRow['format'] == 'MPEG2':
                filename = fileRow['name']
                break

#    print "\n\n\nFilename:", filename

    if not filename:
#        print "No mp4 file found; skipping..."
        print "No .mp4 or .mpeg file found; skipping..."
        return

    folderName = envproperties.TRANSCODE_FOLDER + "/" + secure_filename(folderName)

    # Create named folder if not exists
    if not os.path.exists(folderName):
        os.makedirs(folderName)

    # Download file. Thank you https://blog.archive.org/2011/03/31/how-archive-org-items-are-structured/4
    url = "http://archive.org/download/" + record['identifier'] + "/" + filename
#    print "Download url:", url

    videoFile     = folderName + "/" + filename
    indexOfDot    = videoFile.rfind('.')
    transcodeFile = videoFile[0:indexOfDot] + ".mp3"    # Chop off [mp4,mpeg,whatever] extension and add .mp3 instead.

    print "Transcode file:", transcodeFile

    metadataFile  = transcodeFile  + ".metadata"

    # Download file if not already exists
    if not os.path.exists(videoFile):
        print '\n\n\nDownloading...',
        urllib.urlretrieve(url, videoFile)
        print 'done.\n\n\n'

    # Transcode file to mp3, if not already exists
    if not os.path.exists(transcodeFile):
        # TODO - fix literal pathing; this breaks portability.
        # But if I just use 'ffmpeg', then the subshell doesn't have the same env vars, so command not found... doh
#        cmd = "/root/bin/ffmpeg -i " + shellquote(videoFile) + " -f wav - | lame - " + shellquote(transcodeFile)
        cmd = "/root/bin/ffmpeg -i " + shellquote(videoFile) + " -f mp3 " + shellquote(transcodeFile)

        print "duration cmd:", cmd
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

    # Scan the duration and add to the existing metadata before writing to disk
    # (Yes it's already there coming from archive.org, but it's rounded down to the second. This gives us back the fractions.)
    data['metadata']['duration'] = getDurationFromFile(transcodeFile)

    # Save the metadata (don't check exists; we want to overwrite and get latest data always)
    metadata_file = open(metadataFile, 'w')
    metadata_file.write(JsonTools.ObjToJson(data))
    metadata_file.close()

######################################################################################
#           Main Script
######################################################################################

# 1st batch
masterArray = [ ['Daniel Reskin / Casa de Haha', 'https://archive.org/advancedsearch.php?q=title%3A%28casa%20de%20haha%29%20AND%20collection%3A%28denveropenmedia%29&output=json'],
                ['Lawrence Daniel / 2nd Annual Health Awareness & Educational Symposium Part I', 'https://archive.org/advancedsearch.php?q=title%3A%282nd%20annual%20health%20awareness%20%26%20educational%20symposium%29%20AND%20collection%3A%28denveropenmedia%29&output=json'],
                ['Krystal Covington / Inside the Women of Denver', 'https://archive.org/advancedsearch.php?q=title%3A%28Inside%20the%20women%20of%20denver%29%20AND%20collection%3A%28denveropenmedia%29&output=json'],
                ['Theconsciousviewtv / Living Consciously - TV', 'https://archive.org/advancedsearch.php?q=title%3A%28living%20consciously%29%20AND%20collection%3A%28denveropenmedia%29&output=json'],
                ['cstewart / Chuck and Linda Lee Show', 'https://archive.org/advancedsearch.php?q=title%3A%28linda%20lee%29%20AND%20collection%3A%28denveropenmedia%29&output=json'],
                ['Open Music Sessions',    'https://archive.org/advancedsearch.php?q=title%3A%28Open+Music+Sessions%29+AND+collection%3A%28denveropenmedia%29&output=json'],

# 2nd batch 8/31/16
                ['Amy Goodman', 'https://archive.org/advancedsearch.php?q=title%3A%28amy%20goodman%29%20AND%20collection%3A%28denveropenmedia%29&output=json'],
                ['Bill Freud / Far More Colorado', 'https://archive.org/advancedsearch.php?q=title%3A%28far+more+colorado%29+AND+collection%3A%28denveropenmedia%29&page=2&output=json'],
                ['Maurice / Executive Talk', 'https://archive.org/advancedsearch.php?q=title%3A%28executive%20talk%29%20AND%20collection%3A%28denveropenmedia%29&output=json'],
                ['KGNU Search', 'https://archive.org/advancedsearch.php?q=creator%3A%28KGNU%29%20AND%20collection%3A%28denveropenmedia%29&output=json']
                ]

#https://archive.org/search.php?query=title%3A%28Open+Music+Sessions%29+AND+collection%3A%28denveropenmedia%29&output=json
#https://archive.org/advancedsearch.php?q=title%3A%28Open+Music+Sessions%29+AND+collection%3A%28denveropenmedia%29&output=json

for row in masterArray:
    (folderName, url) = (row[0], row[1])

    print "======================================"
    print "Name: " + folderName
    print "URL:  " + url

    # Call archive.org to get the list of files in the library.
    print "Calling archive.org..."
#    responseObj = urllib2.urlopen(envproperties.ARCHIVE_ORG_QUERY_URL)
    responseObj = urllib2.urlopen(url)
    responseStr = responseObj.read()
#    responseStr = responseStr[9:-1]    # Cutting off the "callback()" part of the response
    #print "Response:", responseStr

    data = json.loads(responseStr)
    data = data['response']

    numFound = data['numFound']
    print "Total Records:", numFound

    allRecords = data['docs']

    temptotal = 0
    for record in allRecords:
        try:
            processRecord(record, folderName)
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            print "Something failed... continuing to next file."

print "Done!"