from __init__ import *

class VoiceRecognizer(multiprocessing.Process):
	def __init__(self,q,homeName = 'Celeste'):
		super(VoiceRecognizer, self).__init__()
		self.recognizer = sr.Recognizer()
		self.q=q
		self.homeName = homeName
		self.config=self.q.get()
		self._message = multiprocessing.Value(c_char_p, '')
		self.running=True
		
		if (self.config==1):
			self.configure()
		else:
			self.start()

	def edit_distance(self, str1, str2):
		m, n = len(str1), len(str2)

		dp = [[0 for x in range(n+1)] for x in range(m+1)]
	 
		for i in range(m+1):
			for j in range(n+1):
	 
				if i == 0:
					dp[i][j] = j    
	 
				elif j == 0:
					dp[i][j] = i    
				elif str1[i-1] == str2[j-1]:
					dp[i][j] = dp[i-1][j-1]
	 
				else:
					dp[i][j] = 1 + min(dp[i][j-1],       
									   dp[i-1][j],       
									   dp[i-1][j-1])    
		return dp[m][n]
	
	@property
	def message(self):
		return self._message.value
	
	@message.getter
	def message(self):
		return self._message.value
		
	@message.setter
	def message(self, txt):
		self._message.value = txt

	def predict(self, controllers):
		h = {}
		for controller in controllers:
			for state in controller.states:
				h[state.name] = self.edit_distance(self.message, state.name)
		result = max(h.iterkeys(), key=(lambda key: h[key]))
		self.q.put(result)
		return result

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
							self.predict()
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

	def configure(self):
		print(self.talkAndWait('Hello user, tell me your name'))
		print(self.talkAndWait('Nice name. What is your favorite color?'))
		self.run()

	
