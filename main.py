#!/usr/bin/env python

# Controller
from core.controllers import *
from core.voice import VoiceCommandClassifier
from core.voice import VoiceRecognizer, VoiceRecognizerModes
import time
import threading
import psycopg2
import sys

global ASSISTANT_NAME
ASSISTANT_NAME = "Celeste"
LEARNING_RATE = 0.2


class MainController(threading.Thread):
    """ This class holds main controller that is responsible for synchronizing the
    rest of the controllers. Due to GIL it is obliged to be a threading.Thread"""

    def __init__(self, controllers):
        super(MainController, self).__init__()
        self.controllers = controllers
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
        self.hashed_states = {}  # TODO hash pairs
        self.running=True
        self.kill=False
        x = 0
        for i in range(len(self.controllers)):
            for j in range(len(self.controllers[i].states)):
                self.hashed_states[i, j] = x
                x += 1


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

    def shutDown(self):
        try:
            for controller in self.controllers:
                controller.terminate()
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

        # main thread body
        while True:
            while self.running:
                pass
            if self.kill:
                return

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True

if __name__ == '__main__':
    main_controller = MainController(
        [DummyController(update_interval=2)])
    main_controller.start()
    time.sleep(3)
    main_controller.shutDown()
