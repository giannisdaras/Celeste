from __init__ import *

global homeName
homeName="home"

class VoiceClassifier(multiprocessing.Process):
	def __init__(self, prefix=homeName):
		super(VoiceClassifier, self).__init__()
		self.running = True
		self.recognizer = sr.Recognizer()
		self.triggered = False #Sets to true when it hears its name
		self.instruction = '' #holds last instruction as string
		self.prefix = prefix

	def rec(self):
		while True:
			while self.running:
				print(1)
				with sr.Microphone() as source:
					self.recognizer.adjust_for_ambient_noise(source)
					audio1 = self.recognizer.listen(source)
					try:
						message=self.recognizer.recognize_google(audio1)
						print('message was: ' + message)
						if (self.prefix in message):
							self.triggered = True
							text=message[message.index(homeName) + len(self.prefix) + 1:]
							self.instruction = text
					except sr.UnknownValueError:
						print('Untracked')
					finally:
						time.sleep(1)
						self.triggered = False

	def run(self):
		self.rec()

	def pause(self):
		self.running = False

	def resume(self):
		self.running = True

# TODO Add feedback analyzer (with textblob)

if __name__ == '__main__':
	voice_classifier = VoiceClassifier()
	voice_classifier.start()
