import keras
from keras.models import Sequential
from keras.layers import Dense, Activation, Convolution2D, MaxPooling2D, Dropout, Flatten
import time
import datetime
import os
import sys
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
