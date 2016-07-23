import os
from gtts import gTTS
import random
import re

# TODO FIXME should some kind of init or setup script run the apt-get install for gtts?

# TODO FIXME we may want to extend profanity's matching text file- It had like 100 entries or less 

DEBUG = False

class TTSTools:

	def __init__(self, title=' an untitled track ', artist=' an unknown artist '):
		"""
		Takes the title and artist name and sets member variables for the class
		Immediately scrapes profanity from the title or artist name to prevent 
		profanity from going out on the radio 
		"""

		# use this list along with a random gen to keep things interesting
		# FIXME perhaps migrate this to a .csv/ .dat/ DB table and read?
		self.sentence_list=['You were listening to 1 by 2',
				    'You just heard 1 by 2',
				    'That last song was 1 by 2',
				    'That track was 1 by 2',
                                    'That was the artist 2 playing 1',
                                    'That last song was 1 by 2']

		self.language = 'en'

		self.text_file = 'profane_words.txt'

		# scrub profanity from title 
		self.artist = artist
		self.title  = title
		self.check_for_profanity()	
	
		self.outro_title = self.title.lstrip().replace(" ", "_")+str(" - OUTRO.mp3")
		self.outro_path = os.getcwd()+'/'+self.outro_title

	def check_for_profanity(self):
		"""
		Checks against the words in the profanity list- 
		will match spaced out or normal words		
		"""
		with open(self.text_file, 'r') as fp:
			bad_words = fp.read().replace(' ', '').split(',')
		
		artist_words = self.artist.lower().split()
		title_words  = self.title.lower().split()

		# check for blatant profanities in artist name
		for a in artist_words:
			if a in bad_words:
				if DEBUG:
					print("BAD!! -> "+ a) 
				self.artist = ' an unknown artist '

		# check for blatant profanities in track name
		for t in title_words:
			if t in bad_words:
				if DEBUG:
					print("BAD!! ->"+ t) 
				self.title = ' an untitled track '

		# check for profanities separated by spaces
		for a in range(len(artist_words)):
			for b in range(a+1,len(artist_words)):
				temp_artist = ''.join(artist_words[a:b+1])
				if DEBUG:
					print temp_artist
				if temp_artist in bad_words:
					if DEBUG:
						print("BAD!! -> "+ temp_artist) 
					self.artist = ' an unknown artist '

		# check for profanities separated by spaces
		for t in range(len(title_words)):
			for v in range(t+1,len(title_words)):
				temp_title = ''.join(title_words[t:v+1])
				if DEBUG:
					print temp_title
				if temp_title in bad_words:
					if DEBUG:
						print("BAD!! -> "+ temp_title) 
					self.title = ' an unnamed track '


	def construct_tts_file(self):
		"""
		Creates the string and then the .mp3 file that will be 
		returned and fed into the RadioDJ db 
		"""
	
		# first choose a random sentence from the list
		outro_string = self.sentence_list[random.randrange(len(self.sentence_list))]
		
		# place the song title at the '1'
		outro_string = re.sub('1',self.title, outro_string)
			
		# place the artist name at the '2'
		outro_string = re.sub('2', self.artist, outro_string)

		if DEBUG == True:
			print(outro_string)
		
		tts=gTTS(text=outro_string, lang=self.language)
		fp = tts.save(self.outro_title)

		self.outro_path = os.getcwd()+'/'+self.outro_title
		
		return self.outro_path

	def cleanup(self):
		"""
		Once the file is in the DB, go ahead and remove it.
		"""
		# FIXME should this first check the DB to ensure the outro is there?
		try:
			os.remove(self.outro_path)
		except:
			print("File was not found!")

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
	tts2.cleanup()
	tts3.cleanup()
