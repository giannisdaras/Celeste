#!/usr/bin/env python

# Controller
from core.controllers import *
from core.voice import VoiceClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
import time
import threading


class MainController(threading.Thread):
    """ This class holds main controller that is responsible for synchronizing the
    rest of the controllers. Due to GIL it is obliged to be a threading.Thread"""

    def __init__(self, controllers, voice_recognizer=VoiceClassifier(), direct_command=False):
        super(MainController, self).__init__()
        self.controllers = controllers
        self.voice_recognizer = voice_recognizer
        self.running = True
        self.direct_command = direct_command
        self.queue = multiprocessing.Queue()  # thread queue
        self.pool = multiprocessing.Pool()
        self.bayesian_classifier = Pipeline([('vect', CountVectorizer()),
                                             ('tfidf', TfidfTransformer(
                                                 use_idf=False)),
                                             ('clf', MultinomialNB()), ])
        self.hashed_states = {}  # TODO hash pairs

        x = 0
        for i in range(len(self.controllers)):
            for j in range(len(self.controllers[i])):
                self.hashed_states[i, j] = x
                x += 1

    def train_classifier(self, x, y):
        self.bayesian_classifier.fit(x, y)

    def changeState(self, i, k, wait_interval=0.5):
        self.controllers[i].state = self.controllers[i].states[k]
        self.controllers[i].state.onActivation(self.controllers[i].getData())
        time.sleep(wait_interval)
        self.controllers[i].resume()

    def joinAll(self):
        for controller in self.controllers:
            controller.join()
        self.voice_recognizer.join()

    def run(self):
        # start all controllers as threads
        for controller in self.controllers:
            controller.start()
        # start voice recognition
        self.voice_recognizer.start()
        # main thread body
        while True:
            while self.running:
                if self.voice_recognizer.triggered:
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

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True


if __name__ == '__main__':
    main_controller = MainController([DummyController(update_interval=10)])
    main_controller.start()
