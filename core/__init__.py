import keras
from keras.models import Sequential
from keras.layers import Dense, Activation, Convolution2D, MaxPooling2D, Dropout, Flatten
import time
import datetime
import os
import sys
import operator
import threading
import inspect
import enum
import multiprocessing
import numpy as np
import cv2
import unittest
import speech_recognition as sr
import threading
from pyfirmata import Arduino, util
from ctypes import c_char_p
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from subprocess import call,Popen
import sys
import spotipy
import spotipy.util as util
from os import system as cmd
import urllib
import webbrowser
from multiprocessing.managers import BaseManager

def edit_distance(str1, str2, weight = lambda s1,s2, i, j: 0.75 if s1[i-1] == ' ' or s2[j-1] == ' ' else 1):
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
					dp[i][j] = weight(str1,str2,i,j) + min(dp[i][j-1],       
									   dp[i-1][j],       
									   dp[i-1][j-1])    
		return dp[m][n]
	


def normalize(x, l=None,r=None):
	x = x.astype('float64')
	if l == None:
		l = np.min(x)
	if r == None:
		r = np.max(x)		
	return (x - l) / (r - l)	
