import speech_recognition as sr
import serial
import threading
import time
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn import preprocessing
from sklearn.model_selection import cross_val_score
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.decomposition import PCA
from sklearn.ensemble import VotingClassifier
from sklearn.metrics import f1_score


def fire():
	fold_numbers=4
	X = np.genfromtxt('training_data.csv', delimiter=',')
	y = np.genfromtxt('training_results.csv', delimiter=',')
	forest=RandomForestClassifier(criterion='entropy',n_estimators=31,n_jobs=1)
	forest.fit(X,y)
	print(forest.predict([10,01,0,0,28]))

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
	    except:
	    	print("No internet connection")
	    	break
fire()

