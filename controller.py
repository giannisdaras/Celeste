import speech_recognition as sr
import serial

def train(command):
	print("Training")
	return

def changeHomeState(command):
	return

def arduino(command):
	#replace with your own port
	ser = serial.Serial('/dev/ttyACM1', 9600)
	ser.write(command)
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
	



