# Python includes
import codecs, random, random, re, os

# Our own package includes
import envproperties

# Third-party includes
from gtts import gTTS

DEBUG = False

class TTSTools:

	def __init__(self, title=None, artist=None, logger=None):
		"""
		Takes the title and artist name and sets member variables for the class
		Immediately scrapes profanity from the title or artist name to prevent 
		profanity from going out on the radio 
		"""

		if title is None:
			raise ValueError("title must be specified")

		if logger:
			self.logger = logger

		# Use this list along with a random gen to keep things interesting
		# FIXME perhaps migrate this to a .csv/ .dat/ DB table and read?
		self.sentence_list=['You were listening to, 1, by 2, on Denver Open Media,',
							'You just heard, 1, by 2, on Denver Open Media,',
							'That last song was, 1, by 2, on Denver Open Media,',
							'That track was, 1, by 2, on Denver Open Media,',
							'That was the artist, 2, playing 1, on Denver Open Media,',
							'That last song was, 1, by 2, on Denver Open Media,']

		# If we don't know the artist, don't reference them:
		if artist is None:
			self.sentence_list = [sentence.replace('by 2, ', '') for sentence in self.sentence_list]
			self.sentence_list = [sentence.replace('the artist, 2, playing ', '') for sentence in self.sentence_list]

		self.language = 'en'

		# scrub profanity from title 
		self.artist = artist
		self.title  = title
		self.check_for_profanity()	

		self.outro_title = self.title.lstrip().replace(" ", "_")+str(" - OUTRO.mp3")
		self.outro_path = os.getcwd()+'/'+self.outro_title

	def log(self, msg):
		if self.logger:
			self.logger.debug("(TTSTools) " + msg)

	def getValidFilename(self, filename):
		keepcharacters = (' ','.','_','-')
		return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()

	def check_for_profanity(self):
		"""
		Checks against the words in the profanity list- 
		will match spaced out or normal words		
		"""

		# Fix needed in conjunction with allowing null artists
		# Also wash the dash from the inputs; for some reason it trips the profanity check
		title  = self.title.replace('-', '')
		artist = ''
		if self.artist:
			artist = self.artist.replace('-', '')

		encoded_words = envproperties.ENC_PROFANITY
		
		bad_words = []
		for i in encoded_words:
			bad_words.append(codecs.decode(i, 'rot_13'))
		
		artist_words = artist.lower().split()
		title_words  = title.lower().split()

		# check for blatant profanities in artist name
		for a in artist_words:
			if a in bad_words:
				self.log("BAD!! -> "+ a) 
				artist = ' an unknown artist '

		# check for blatant profanities in track name
		for t in title_words:
			if t in bad_words:
				self.log("BAD!! ->"+ t) 
				title = ' an untitled track '

		# check for profanities separated by spaces
		for a in range(len(artist_words)):
			for b in range(a+1,len(artist_words)):
				temp_artist = ''.join(artist_words[a:b+1])
				if DEBUG:
					self.log(temp_artist)
				if temp_artist in bad_words:
					self.log("BAD!! -> "+ temp_artist) 
					artist = ' an unknown artist '

		# check for profanities separated by spaces
		for t in range(len(title_words)):
			for v in range(t+1,len(title_words)):
				temp_title = ''.join(title_words[t:v+1])
				if DEBUG:
					self.log(temp_title)
				if temp_title in bad_words:
					self.log("BAD!! -> "+ temp_title) 
					title = ' an unnamed track '

	def construct_tts_file(self):
		"""
		Creates the string and then the .mp3 file that will be 
		returned and fed into the RadioDJ db 
		"""

		# first choose a random sentence from the list
		outro_string = self.sentence_list[random.randrange(len(self.sentence_list))]

		# place the song title at the '1'
		outro_string = re.sub('1', self.title, outro_string)

		# place the artist name at the '2'
		if self.artist:
			outro_string = re.sub('2', self.artist, outro_string)

		if DEBUG == True:
			self.log(outro_string)

		tts=gTTS(text=outro_string, lang=self.language)

		fileName = self.getValidFilename(self.outro_title)
		fp = tts.save(fileName)

		self.outro_path = os.getcwd()+'/'+fileName
		return self.outro_path

	def cleanup(self):
		"""
		Once the file is in the DB, go ahead and remove it.
		"""
		# FIXME should this first check the DB to ensure the outro is there?
		try:
			os.remove(self.outro_path)
		except:
			self.log("File was not found!")

# dunno if we should keep this check, maybe not
if __name__ == "__main__":
	"""
	Test a profane, a weird, and an acceptable track name
	"""
	
	artist1 = "the good people"
	track1  = " a happy song"

	artist2 = " F u c k everyone"
	track2  = " the shit head fuckers "

	artist3 = " //--== "
	track3  = " Oiuouiuiuiausd "

	tts1 = TTSTools(track1, artist1)
	tts2 = TTSTools(track2, artist2)
	tts3 = TTSTools(track3, artist3)

	tts1.construct_tts_file()
	tts2.construct_tts_file()
	result = tts3.construct_tts_file()
	if DEBUG:
		print result

	tts1.cleanup()
#	tts2.cleanup()
	tts3.cleanup()
