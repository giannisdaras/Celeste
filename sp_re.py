import speech_recognition as sr

r1 = sr.Recognizer()
with sr.Microphone() as source:
    r1.adjust_for_ambient_noise(source)  # listen for 1 second to calibrate the energy threshold for ambient noise levels
    print("Say something!")
    audio1 = r1.listen(source)

if "ok" in r1.recognize_google(audio1):
	r2 = sr.Recognizer()
	with sr.Microphone() as source:
		r2.adjust_for_ambient_noise(source)  # listen for 1 second to calibrate the energy threshold for ambient noise levels 
		print("Now give an order!")
		audio2 = r2.listen(source)
	try:
   		print("You probably said: " + r2.recognize_google(audio2))
	except sr.UnknownValueError:
   		print("Sorry, i didn't quite catch that")
	except sr.RequestError as e:
		print("Could not request results from Google Speech Recognition service; {0}".format(e))

else:
	print("No response")
	
