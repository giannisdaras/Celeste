# Controller
from core.controllers import *
from core.state_predictor import StatePredictor
from core.voice import VoiceClassifier
import time
import threading
import word2vec as w2v

class MainController(threading.Thread):

    def __init__(self, controllers, voice_recognizer, vocabulary_path='', direct_command=False):
        super(MainController, self).__init__()
        self.controllers = controllers
        self.voice_recognizer = voice_recognizer
        self.running = True
        self.direct_command = direct_command
        self.queue = multiprocessing.Queue() #thread queue

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
                    # TODO use sentiment analysis with word2vec

                    if self.direct_command:
                        for controller in self.controllers:
                            for k in controller.states.keys():
                                if controller.states[k].name == voice_recognizer.instruction:
                                    print 'Voice command alters state to: ' + controller.states[k].name
                                    controller.state = controller.states[k]
                                    controller.state.onActivation(controller.getData())
                                    time.sleep(2)
                                    controller.resume()

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True

if __name__ == '__main__':
    main_controller = MainController([StatePredictor.DummyStatePredictor(update_interval=10)], VoiceClassifier())
    main_controller.start()
