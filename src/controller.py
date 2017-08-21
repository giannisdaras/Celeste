import speech_recognition as sr
import serial
import threading
import time
import numpy as np

global homeName
homeName="home"

def fire():
	return

class VoiceClassifier():
	def __init__(self):
		self.recognizer = sr.Recognizer()
		return
	def rec(self):
		while(True):
			print(1)
			with sr.Microphone() as source:
			    self.recognizer.adjust_for_ambient_noise(source)
			    audio1 = self.recognizer.listen(source)
			    try:
			    	message=self.recognizer.recognize_google(audio1)
			    	print('message was: ' + message)
			    	if (homeName in message):
				    	text=message[message.index(homeName) + len(homeName) + 1:]
				    	if ("training" in text):
				    		train(text)
			    except sr.UnknownValueError:
			    	print('Untracked')
			    except:
			    	continue
		return
		

class VoiceThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.recorder=VoiceClassifier()
	def run(self):
		self.recorder.rec()
		return

def train(command):
	print("Training")
	return

def changeHomeState(command):
	return

voice_thread=VoiceThread()
voice_thread.start()










