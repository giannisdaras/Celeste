import speech_recognition as sr

def train(command):
	print(text)
	return

def changeHomeState(command):
	return

homeName="home"
recognizer = sr.Recognizer()
while(True):
	with sr.Microphone() as source:
	    recognizer.adjust_for_ambient_noise(source)
	    recognizer.energy_threshold=500
	    audio1 = recognizer.listen(source)
	    try:
	    	message=recognizer.recognize_google(audio1)
	    	print(message)
	    	text=message[message.index(homeName) + len(homeName) + 1:]
	    	if ("training" in text):
	    		train(text)
	    except sr.UnknownValueError:
	    	print("did not hear")
	



