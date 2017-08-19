import speech_recognition as sr
import serial
import threading
import time


def fire():
	#event fired
	return

class foo(threading.Thread):
	#basic thread function!
	def run(self):
		time.sleep(2)
		eventFlag=checkForEvent()
		if (eventFlag==1):
			eventFlag=0
			fire()
	def checkForEvent(self):
		return 0


class Arduino:
	def __init__(self):
		x = 0
		for x in range(10):
			try:
				#check if ports work
				self.ser = serial.Serial('/dev/ttyACM{0}'.format(x), 9600)
				return
			except:
				continue
		print('No port found')

	def command(self, cmd):
		self.ser.write(cmd)			

	def __del__(self):
		self.ser.close()

def train(command):
	print("Training")
	return

def changeHomeState(command):
	return


homeName="home"
recognizer = sr.Recognizer()
while(True):
	with sr.Microphone() as source:
	    recognizer.adjust_for_ambient_noise(source)
	    audio1 = recognizer.listen(source)
	    try:
	    	message=recognizer.recognize_google(audio1)
	    	if (homeName in message):
		    	text=message[message.index(homeName) + len(homeName) + 1:]
		    	if ("training" in text):
		    		train(text)
	    except sr.UnknownValueError:
	    	print("Untracked sound")
	



