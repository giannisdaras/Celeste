#!/usr/bin/env python

# Controller
from core.controllers import *
from core.voice import VoiceCommandClassifier
from core.voice import VoiceRecognizer, VoiceRecognizerModes
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
import time
import threading
import psycopg2
import sys
import pyttsx
import pyaudio

global ASSISTANT_NAME
ASSISTANT_NAME = "Celeste"
LEARNING_RATE = 0.2


class MainController(threading.Thread):
    """ This class holds main controller that is responsible for synchronizing the
    rest of the controllers. Due to GIL it is obliged to be a threading.Thread"""

    def __init__(self, controllers, voice_recognizer=VoiceRecognizer(), direct_command=False):
        super(MainController, self).__init__()
        self.controllers = controllers
        self.voice_recognizer = voice_recognizer
        self.voice_recognizer_queue = multiprocessing.Queue()
        self.voice_recognizer.queue = self.voice_recognizer_queue

        self.running = True
        self.kill = False

        self.direct_command = direct_command

        self.bayesian_classifier = Pipeline([('vect', CountVectorizer()),
                                             ('tfidf', TfidfTransformer(
                                                 use_idf=False)),
                                             ('clf', MultinomialNB()), ])

        # DB connection
        try:
            self.conn = psycopg2.connect(
                "dbname='Celeste' user='postgres' host='localhost' password='1234'")
        except:
            raise Exception('Could not find database. Exiting now')
            sys.exit(1)
        self.cur = self.conn.cursor()
        self.cur.execute('select * from settings')
        self.first_time = self.cur.fetchall()[0]
        if (self.first_time):
            self.configure()

        self.hashed_states = {}  # TODO hash pairs
        x = 0
        for i in range(len(self.controllers)):
            for j in range(len(self.controllers[i].states)):
                self.hashed_states[i, j] = x
                x += 1

    def train_classifier(self, x, y):
        self.bayesian_classifier.fit(x, y)

    def changeState(self, i, k, wait_interval=0.5):
        self.controllers[i].state = self.controllers[i].states[k]
        self.controllers[i].state.onActivation(self.controllers[i].getData())
        time.sleep(wait_interval)
        y = keras.utils.to_categorical(k, self.constrollers[i].num_classes)

        n = int(LEARNING_RATE * self.controllers[i].num_train)
        x = self.constrollers[i].getData()
        for i in range(n):
            self.constrollers[i].model.train_on_batch(np.array([x]), y)
        self.controllers[i].num_train += n
        self.controllers[i].resume()

    def joinAll(self):
        for controller in self.controllers:
            controller.join()
        self.voice_recognizer.join()

    def shutDown(self):
        try:
            for controller in self.controllers:
                controller.terminate()
            self.voice_recognizer.terminate()
            self.joinAll()
            self.pause()
            self.kill = True
            super(MainController, self).join()
            print 'Terminated everything'
            return True
        except:
            return False

    def run(self):
        # start all controllers as threads
        for controller in self.controllers:
            controller.start()

        # start voice recognition
        if (not self.first_time):
            self.voice_recognizer.start()
        else:
            self.voice_recognizer.resume()

        # main thread body
        while True:
            while self.running:
                if self.voice_recognizer.triggered and self.voice_recognizer.mode == VoiceRecognizerModes.COMMAND:
                    print 'Stop State Prediction and to force voice command'
                    # Find corresponding state

                    if self.direct_command:
                        for (i, controllers) in enumerate(self.controllers):
                            for k in controller.states.keys():
                                if controller.states[k].name == voice_recognizer.instruction:
                                    self.changeState(i, k)
                    else:
                        y = self.bayesian_classifier.predict(
                            voice_recognizer.instruction)
                        try:
                            self.changeState(*self.hashed_states[y])
                        except KeyError:
                            print 'Command not found'
                            continue
            if self.kill:
                return

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True

    def talk(self, text):
        obj = pyttsx.init()
        obj.setProperty('rate', obj.getProperty('rate') - 45)
        obj.setProperty('voice', 'english+f4')
        obj.say(text)
        obj.runAndWait()
        del obj
        time.sleep(0.5)
        return

    @property
    def instruction(self):
        self.voice_recognizer_queue.get().split(' ')

    @instruction.getter
    def instruction(self):
        return self.voice_recognizer_queue.get().split(' ')

    def configure(self):
        self.voice_recognizer.mode = VoiceRecognizerModes.RECORD
        self.talk("Hello, user! What is your favourite color?")
        self.voice_recognizer.start()
        time.sleep(10)
        print('Instruction')
        print(self.instruction)
        # self.talk("But first let me introduce myself. My name is {0}; your new smart home assistant".format(
        #     ASSISTANT_NAME))
        # self.talk(
        #     "You will soon realize that you need to care almost for nothing cause this smart home behaves in an exciting way")
        # self.talk(
        #     "Everything is tailor-made tou your habbits and automated tasks will take place all of the time")
        # self.talk("So relax and let the fun begin!")

        # Do some configuration stuff

        # alter mode to command mode
        self.voice_recognizer.pause()
        #self.voice_recognizer.mode = VoiceRecognizerModes.COMMAND


class MainControllerUnittest(unittest.TestCase):

    def setUp(self):
        self.main_controller = MainController(
            [DummyController(update_interval=2)])

    def test_dummy(self):
        self.main_controller.start()
        time.sleep(10)
        self.main_controller.shutDown()


if __name__ == '__main__':
    main_controller = MainController(
        [DummyController(update_interval=2)])
    main_controller.start()
    time.sleep(3)
    main_controller.shutDown()
