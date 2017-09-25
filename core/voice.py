from __init__ import *

class VoiceRecognizer(multiprocessing.Process):
	def __init__(self,q,homeName = 'Celeste'):
		super(VoiceRecognizer, self).__init__()
		self.recognizer = sr.Recognizer()
		self.q= q
		self.homeName = homeName
		self.config=self.q.get()[0]
		self._message = multiprocessing.Value(c_char_p, '')
		self.running = True
		self.property_keys = ['name', 'color', 'music', 'category']
		
		if (self.config==1):
			self.configure()
		else:
			self.start()

	@property
	def message(self):
		return self._message.value
	
	@message.getter
	def message(self):
		return self._message.value
		
	@message.setter
	def message(self, txt):
		self._message.value = txt

	def recordOnce(self):
		with sr.Microphone() as source:
			self.recognizer.adjust_for_ambient_noise(source)
			while(True):
				audio1 = self.recognizer.listen(source)
				try:
					self.message = self.recognizer.recognize_google(audio1)
					break
				except sr.UnknownValueError:
					self.talk('Please repeat')
		return(self.message)
					
	def run(self):
		while True:
			while self.running:
				with sr.Microphone() as source:
					self.recognizer.adjust_for_ambient_noise(source)
					audio1 = self.recognizer.listen(source)
					try:
						self.message = self.recognizer.recognize_google(audio1)
						if ('Celeste' in message):
							self.message = self.message.strip(self.homeName)
							self.talk('You said {0}'.format(message))
							self.q.put(self.message)
					except sr.UnknownValueError:
						self.message = ''
					finally:
						time.sleep(1)
	

	def pause(self):
		self.running = False

	def resume(self):
		self.running = True

	def talkAndWait(self,text):
		f=Popen("google_speech -l en '{0}'".format(text), shell=True)
		f.wait()
		del f
		return(self.recordOnce())
		
	def talk(self,text):
		f=Popen("google_speech -l en '{0}'".format(text), shell=True)
		f.wait()
		del f
		self.running = True

	def addPerson(self, i):
		answers = []
		for key in self.property_keys:
			answers.append("'{}'".format(self.talkAndWait(key)))
		
		# Prepare POSTGRES COMMAND
		query = "INSERT INTO (id,{}) people VALUES ({},{})".format(','.join(self.property_keys), i, ','.join(answers))
		self.q.put(query)
		

	def configure(self):
		i = 0
		while True:
			ans = self.talkAndWait('Add {} user?'.format('another' if i > 0 else ''))
			if edit_distance(ans, 'yes') < edit_distance(ans, 'no'):
				self.addPerson(i)
				i += 1
			else:
				break
