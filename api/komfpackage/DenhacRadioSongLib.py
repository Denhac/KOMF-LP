#!/usr/bin/python

# Python includes
import datetime, grp, logging, logging.handlers, os, pwd, subprocess, urllib

# Our own package includes
from komfpackage import envproperties, JsonTools, DenhacDb, DenhacRadioDjDb, TTSTools

# Third-party includes
import eyed3

class RadioSongLib:

    def __init__(self):
        self.totalRows           = 0
        self.totalNewFiles       = 0
        self.filesMovedToLibrary = 0
        self.filesMovedToStaging = 0

        self.radioDj = DenhacRadioDjDb()
        self.uid     = pwd.getpwnam(envproperties.APACHE_USER_NAME).pw_uid
        self.gid     = grp.getgrnam(envproperties.APACHE_GROUP_NAME).gr_gid

    def setAppLogger(self):
        self.appLogger = logging.getLogger('ImportLogger')
        self.appLogger.propagate = False

        # TODO - revert to INFO once we're stable
        #appLogger.setLevel(logging.INFO)
        self.appLogger.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        handler = logging.handlers.RotatingFileHandler(envproperties.IMPORT_LOG_FILE, maxBytes=1024 * 1024 * 10, backupCount=20)
        handler.setFormatter(formatter)

        self.appLogger.addHandler(handler)
        return self.appLogger

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
        cmd = "/root/bin/ffprobe -i " + RadioSongLib.shellquote(filePath) + " -show_entries format=duration -v quiet -of csv=\"p=0\""
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        duration = proc.stdout.read()
        return duration[:-4]    # Reduce from 7 decimal places to 3

    def getCueTimesFromDuration(duration):
        return "&sta=0&xta=" + str(float(duration) - float(envproperties.FADE_OUT_SEC)) + "&end=" + duration + "&fin=" + str(envproperties.FADE_IN_SEC) + "&fou=" + str(envproperties.FADE_OUT_SEC)

    def getFilenameFromUrl(url):
        fileName = url.rsplit('/', 1)[-1]
        fileName = urllib.unquote(fileName).decode('utf8')
        fileName = os.path.normpath(fileName)
        return fileName

    def getMetadataFromCsvRow(row):
        metadata = dict()

#        metadata['title']         = str(row['Title'])
#        metadata['fileurl']       = str(row['Audio File'])
#        metadata['theme']         = str(row['Theme'])
#        metadata['genre']         = str(row['Genre'])
#        metadata['broadcastFlag'] = str(row['Authorized for Broadcast'])
#        metadata['indecencyFlag'] = str(row['Indecent Content'])
        metadata['title']         = ''
        metadata['fileurl']       = ''
        metadata['theme']         = ''
        metadata['genre']         = ''
        metadata['artist']        = ''
        metadata['broadcastFlag'] = ''
        metadata['indecencyFlag'] = ''

        # This if/elif craziness is because columns/data can sometimes have quotes, sometimes not, without warning

        # Title
        if 'Title' in row:
            metadata['title'] = str(row['Title'])
        elif '"Title"' in row:
            metadata['title'] = str(row['"Title"'])
        elif '\"Title\"' in row:
            metadata['title'] = str(row['\"Title\"'])
        else:
            raise KeyError("Title column not found!")

        # Audio File (URL/location)
        if 'Audio File' in row:
            metadata['fileurl'] = str(row['Audio File'])
        elif '"Audio File"' in row:
            metadata['fileurl'] = str(row['"Audio File"'])
        elif '\"Audio File\"' in row:
            metadata['fileurl'] = str(row['\"Audio File\"'])
        else:
            raise KeyError("Audio File column not found!")

        if metadata['fileurl'] == '':
            raise KeyError("No data in Audio File column!")

        # Theme
        if 'Theme' in row:
            metadata['theme'] = str(row['Theme'])
        elif '"Theme"' in row:
            metadata['theme'] = str(row['"Theme"'])
        elif '\"Theme\"' in row:
            metadata['theme'] = str(row['\"Theme\"'])
        else:
            raise KeyError("Theme column not found!")

        # Genre
        if 'Genre' in row:
            metadata['genre'] = str(row['Genre'])
        elif '"Genre"' in row:
            metadata['genre'] = str(row['"Genre"'])
        elif '\"Genre\"' in row:
            metadata['genre'] = str(row['\"Genre\"'])
        else:
            raise KeyError("Genre column not found!")

        # Artist
        # Exception for one old column name:
        if 'Artist/Production Company/Band' in row:
            metadata['artist'] = str(row['Artist/Production Company/Band'])
        elif 'Production Company / Band' in row:
                metadata['artist'] = str(row['Production Company / Band'])
        elif '"Production Company / Band"' in row:
            metadata['artist'] = str(row['"Production Company / Band"'])
        elif '\"Production Company / Band\"' in row:
            metadata['artist'] = str(row['\"Production Company / Band\"'])
        else:
            raise KeyError("Production Company / Band column not found!")

        # Authorized for Broadcast
        if 'Authorized for Broadcast' in row:
            metadata['broadcastFlag'] = str(row['Authorized for Broadcast'])
        elif '"Authorized for Broadcast"' in row:
            metadata['broadcastFlag'] = str(row['"Authorized for Broadcast"'])
        elif '\"Authorized for Broadcast\"' in row:
            metadata['broadcastFlag'] = str(row['\"Authorized for Broadcast\"'])
        else:
            raise KeyError("Authorized for Broadcast column not found!")

        # Indecent Content
        if 'Indecent Content' in row:
            metadata['indecencyFlag'] = str(row['Indecent Content'])
        elif '"Indecent Content"' in row:
            metadata['indecencyFlag'] = str(row['"Indecent Content"'])
        elif '\"Indecent Content\"' in row:
            metadata['indecencyFlag'] = str(row['\"Indecent Content\"'])
        else:
            raise KeyError("Indecent Content column not found!")


        # Handle optional fields
        metadata['postdate'] = ''
        metadata['outroUrl'] = ''
        metadata['album']    = ''
        metadata['bayesian'] = 0.0
        metadata['mean']     = 0.0

        if 'Post date' in row:
            metadata['postdate'] = str(row['Post date'])
        elif '"Post date"' in row:
            metadata['postdate'] = str(row['"Post date"'])
        elif '\"Post date\"' in row:
            metadata['postdate'] = str(row['\"Post date\"'])

#        if 'DJ Outro' in row:
#            metadata['outroUrl'] = str(row['DJ Outro'])
        # DJ Outro
        if 'DJ Outro' in row:
            metadata['outroUrl'] = str(row['DJ Outro'])
        elif '"DJ Outro"' in row:
            metadata['outroUrl'] = str(row['"DJ Outro"'])
        elif '\"DJ Outro\"' in row:
            metadata['outroUrl'] = str(row['\"DJ Outro\"'])

#        if 'Album/Project' in row:
#            metadata['album']    = str(row['Album/Project'])
        if 'Album/Project' in row:
            metadata['album'] = str(row['Album/Project'])
        elif '"Album/Project"' in row:
            metadata['album'] = str(row['"Album/Project"'])
        elif '\"Album/Project\"' in row:
            metadata['album'] = str(row['\"Album/Project\"'])

#        if 'Bayesian Score' in row:
#            metadata['bayesian'] = float(row['Bayesian Score'])
        if 'Bayesian Score' in row:
            metadata['bayesian'] = str(row['Bayesian Score'])
        elif '"Bayesian Score"' in row:
            metadata['bayesian'] = str(row['"Bayesian Score"'])
        elif '\"Bayesian Score\"' in row:
            metadata['bayesian'] = str(row['\"Bayesian Score\"'])

#        if 'Vote!' in row:
#            metadata['mean']     = float(str(row['Vote!']).replace('%', ''))
        # Remove % if it exists (it comes and goes...)
        if 'Vote!' in row:
            metadata['mean'] = str(row['Vote!']).replace('%', '')
        elif '"Vote!"' in row:
            metadata['mean'] = str(row['"Vote!"']).replace('%', '')
        elif '\"Vote!\"' in row:
            metadata['mean'] = str(row['\"Vote!\"']).replace('%', '')

        # Convert to float (and fill in blanks with 0.0)
        if metadata['mean'] == '':
            metadata['mean'] = 0.0
        else:
            metadata['mean'] = float(metadata['mean'])


        # Additional columns currently in the csv, but not in the mapping:
        # ^@"Album Cover"^@, "Logo", "Link"

        # Set year to the current year at the time of import, TODO - until we can get this value from the csv
        metadata['year'] = datetime.datetime.now().year

        # Unknown fields at this time but required by RadioDJ DB - TODO, get these fields from the csv one day
        metadata['copyright'] = "Unknown Copyright"
        metadata['publisher'] = "Unknown Publisher"
        metadata['composer'] = "Unknown Composer"

        # Set the URL-decoded filename and various necessary paths
        fileName = RadioSongLib.getFilenameFromUrl(metadata['fileurl'])

        outroFileName = ''
        if metadata['outroUrl']:
            outroFileName = RadioSongLib.getFilenameFromUrl(metadata['outroUrl'])
        else:
            outroFileName = fileName[:-4] + ' - OUTRO.mp3'

        metadata['fileName']          = fileName
        metadata['outroFileName']     = outroFileName
        metadata['stagingPath']       = RadioSongLib.getStagingPath(fileName)
        metadata['libraryPath']       = RadioSongLib.getLibraryPath(fileName)
        metadata['frontendPath']      = RadioSongLib.getFrontendPath(fileName)
        metadata['targetPath']        = metadata['stagingPath']
        metadata['outroPath']         = RadioSongLib.getStagingPath(metadata['outroFileName'])
        metadata['outroFrontendPath'] = RadioSongLib.getFrontendPath(metadata['outroFileName'])
        if metadata['broadcastFlag']  == 'Yes':
            metadata['targetPath']    = metadata['libraryPath']
            metadata['outroPath']     = RadioSongLib.getLibraryPath(metadata['outroFileName'])

        return metadata

    def moveFilesIfBroadcastFlagChanged(self, metadata):
        # If song exists in library, and Broadcast = No, move it (and its metadata) back to staging
        if os.path.exists(metadata['libraryPath']) and metadata['broadcastFlag'] == 'No':
            self.appLogger.debug("Broadcast disabled; moving file to " + metadata['stagingPath'])

            os.rename(metadata['libraryPath'], metadata['stagingPath'])
            self.filesMovedToStaging += 1
            # Move metadata
            if os.path.exists(metadata['libraryPath'] + '.metadata'):
                os.rename(metadata['libraryPath'] + '.metadata', metadata['stagingPath'] + '.metadata')
            # Move outro
            if os.path.exists(RadioSongLib.getLibraryPath(metadata['outroFileName'])):
                os.rename(RadioSongLib.getLibraryPath(metadata['outroFileName']), RadioSongLib.getStagingPath(metadata['outroFileName']))

        # If song exists in staging, and Broadcast = Yes, move it (and its metadata) to the library
        elif os.path.exists(metadata['stagingPath']) and metadata['broadcastFlag'] == 'Yes':
            self.appLogger.debug("Broadcast enabled; moving file to " + metadata['libraryPath'])

            os.rename(metadata['stagingPath'], metadata['libraryPath'])
            self.filesMovedToLibrary += 1
            # Move metadata
            if os.path.exists(metadata['stagingPath'] + '.metadata'):
                os.rename(metadata['stagingPath'] + '.metadata', metadata['libraryPath'] + '.metadata')
            # Move outro
            if os.path.exists(RadioSongLib.getStagingPath(metadata['outroFileName'])):
                os.rename(RadioSongLib.getStagingPath(metadata['outroFileName']), RadioSongLib.getLibraryPath(metadata['outroFileName']))

    def downloadSong(self, metadata):
        # If song exists in library, and broadcast = Yes, nothing to do
        if os.path.exists(metadata['libraryPath']) and metadata['broadcastFlag'] == 'Yes':
            return

        # If song exists in staging, and broadcast = No, nothing to do
        if os.path.exists(metadata['stagingPath']) and metadata['broadcastFlag'] == 'No':
            return

        # Otherwise, download the file to the correct target diretory, & set owner
        self.appLogger.debug("Downloading new file: " + metadata['targetPath'])
        RadioSongLib.downloadFile(metadata['fileurl'], metadata['targetPath'])
        os.chown(metadata['targetPath'], self.uid, self.gid)
        self.totalNewFiles += 1
        self.appLogger.debug("Download complete.")

    def downloadOrGenerateOutro(self, metadata):
        # If an outro file already exists from a previous run, nothing to do
        if os.path.exists(metadata['outroPath']):
            return

        outroFile = ''
        # If an Outro is defined in the csv file, download and use that one
        if metadata['outroUrl']:
            outroFile = RadioSongLib.downloadFile(metadata['outroUrl'], metadata['outroFileName'])
            self.appLogger.debug("Outro downloaded: " + metadata['outroFileName'])

        # If there is no outro URL, then create an outro and move it to the correct location
        else:
            self.appLogger.debug("Generating Outro: " + metadata['outroFileName'])

            tts1 = None
            if metadata['artist']:
                tts1 = TTSTools(title=metadata['title'], artist=metadata['artist'], logger=self.appLogger)
            else:
                tts1 = TTSTools(title=metadata['title'], logger=self.appLogger)

            outroFile = tts1.construct_tts_file()
            self.appLogger.debug("Outro generated.")

        # Move it to the correct target directory, set correct permissions and track the count
        os.rename(outroFile, metadata['outroPath'])
        os.chown(metadata['outroPath'], self.uid, self.gid)
        self.totalNewFiles += 1

    def updateMetadataFromId3(self, metadata):
        # Calculate duration in seconds and set in metadata
        metadata['duration']        = RadioSongLib.getDurationFromFile(metadata['targetPath'])
        metadata['outro_duration']  = RadioSongLib.getDurationFromFile(metadata['outroPath'])

        # RadioDJ really likes having cue_times... dunno why it can't calculate it itself from the duration (like it does during a manual import), but whatever.
        metadata['cue_times']       = RadioSongLib.getCueTimesFromDuration(metadata['duration'] )
        metadata['outro_cue_times'] = RadioSongLib.getCueTimesFromDuration(metadata['outro_duration'] )

        # For each of the following fields: artist, album, genre:
        #     If DOM is missing value, but mp3 ID3 has it, use ID3 tag
        #     If DOM value exists but mp3 ID3 tag does not have it, save DOM's value to ID3 tag
        #     else set to Unknown

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
        genre_id  = self.radioDj.getGenreIdByName(metadata['genre'])
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
                self.appLogger.debug("Saved new ID3 tag: " + metadata['targetPath'])
            except NotImplementedError:        # eyed3 fails to write ID3 v2.2 tags; ignore
                pass

        return metadata

    def saveMetadataToFile(self, metadata):
        # Write the metadata to the filesystem & set owner
        # This will overwrite file every time to pick up changes; which we want
        abs_path = metadata['targetPath'] + ".metadata"
        metadata_file = open(abs_path, 'w')

        jsonStr = JsonTools.ObjToJson(metadata)
        metadata_file.write(str(jsonStr))
        metadata_file.close()

        os.chown(abs_path, self.uid, self.gid)

    def writeToDB(self, metadata):
        genre_id  = self.radioDj.getGenreIdByName(metadata['genre'])
        subcat_id = self.radioDj.getSubcategoryIdByName(metadata['theme'])

        # Set certain defaults that may be changed if we have an Indecent file
        enabled      = 1
        comments     = ''
        title        = metadata['title']
        play_limit   = 0
        limit_action = 0
        indecent     = 0

        if metadata['indecencyFlag'] == "Yes":
            enabled      = 0
            comments     = "Importing with enabled = OFF due to Indecent content.  Change flag manually to schedule."
            title       += " - EXPLICIT"
            play_limit   = 1
            limit_action = 1
            indecent = 1

        self.radioDj.upsertSongs(metadata['frontendPath'],
                            song_type    = 0,            # Regular songs are 0 (See Dave's email)
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

        # April 2020 - handle post date from .csv
        if len(metadata['postdate']) > 0:
            metadata['postdate'] = datetime.datetime.strptime(metadata['postdate'][0:10], "%m/%d/%Y").date()
        else:
            metadata['postdate'] = None

        # Write extended data - stuff from the audio.csv that does not have a default place in RadioDJ
        row = self.radioDj.getSongByPath(metadata['frontendPath'])
        self.radioDj.setSongExtended(row['ID'], metadata['bayesian'], metadata['mean'], indecent, metadata['postdate'])

        # Outro files always exist by this point now
        self.radioDj.upsertSongs(metadata['outroFrontendPath'],
                            song_type    = 2,        # Outros should be type 2.
                            id_subcat    = 19,        # 19 for Sweeper / Outro
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

    def handleBroadcastFlag(self, metadata):
        # If broadcastFlag is Yes, then insert into RadioDJ DB
        if metadata['broadcastFlag'] == 'Yes':
            self.writeToDB(metadata)
        # Otherwise remove the file and its outro from the DB
        else:
            self.radioDj.deleteSong(metadata['frontendPath'])
            self.radioDj.deleteSong(metadata['outroFrontendPath'])

    def constantMaintenance(self):
        # Call the URL to ask RadioDJ to refresh its Events list (so that other users with separate RadioDJ front ends can create schedules. (This triggers the master RadioDJ instance to refresh them.)
        # TODO - move this URL to envprops
        response = urllib.urlopen("http://192.168.22.16:8080/opt?auth=104.7lpfm&command=RefreshEvents")
        responseText = response.read()
        self.appLogger.debug("Refresh events response: " + responseText)

        # Update any P:\ paths to \\<address> network path instead (fixes issues caused by manual uploads as opposed to automated imports)
        self.radioDj.autoUpdatePath()

    def printCounts(self):
        if self.totalRows > 0:
            self.appLogger.debug("Total rows analyzed: " + str(self.totalRows))
        if self.totalNewFiles > 0:
            self.appLogger.info("Total new files downloaded/generated: " + str(self.totalNewFiles))
        if self.filesMovedToLibrary > 0:
            self.appLogger.info("Total files approved and moved to library: " + str(self.filesMovedToLibrary))
        if self.filesMovedToStaging > 0:
            self.appLogger.info("Total files un-approved and moved back to staging: " + str(self.filesMovedToStaging))

    # Python 2.x way of declaring static functions
    downloadFile             = staticmethod(downloadFile)
    getLibraryPath           = staticmethod(getLibraryPath)
    getStagingPath           = staticmethod(getStagingPath)
    getFrontendPath          = staticmethod(getFrontendPath)
    shellquote               = staticmethod(shellquote)
    getDurationFromFile      = staticmethod(getDurationFromFile)
    getCueTimesFromDuration  = staticmethod(getCueTimesFromDuration)
    getFilenameFromUrl       = staticmethod(getFilenameFromUrl)
    getMetadataFromCsvRow    = staticmethod(getMetadataFromCsvRow)
