import speech_recognition as sr
homeName="smart"
while(True):
	recognizer = sr.Recognizer()
	try:
		with sr.Microphone() as source:
		    recognizer.adjust_for_ambient_noise(source)
		    message=recognizer.recognize_google(audio1)
		    if (homeName in message):
		    	text=message[message.index(homeName) + len(homeName):]
		    	if ("training" in text):
		    		train(text)
		    	else:
		    		changeHomeState(text)
	except:
		print("Check your connection")

def train(command):
	return

def changeHomeState(command):
	return

