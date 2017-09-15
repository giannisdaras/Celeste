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
from PyMata.pymata import PyMata
from ctypes import c_char_p
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from subprocess import call,Popen


def normalize(x, (l,r)=(None,None)):
	x = x.astype('float64')
	if l == None:
		l = np.min(x)
	if r == None:
		r = np.max(x)		
	return (x - l) / (r - l)	
