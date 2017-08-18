import speech_recognition as sr
homeName="smart"
while(True):
	recognizer = sr.Recognizer()
	try:
		with sr.Microphone() as source:
		    recognizer.adjust_for_ambient_noise(source)
		    message=recognizer.recognize_google(audio1)
		    if (homeName in message):
		    	command=message[message.index(homeName) + len(homeName):]
	except:
		print("Check your connection")
	
