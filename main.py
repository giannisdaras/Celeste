# Controller
from ml.state_predictor import StatePredictor
from ml.voice import VoiceClassifier
import time
import threading
import word2vec as w2v

class MainController(threading.Thread):

    def __init__(self, controllers, voice_recognizer, vocabulary_path):
        super(self, MainController).__init__()
        self.controllers = controllers
        self.voice_recognizer = voice_recognizer
        self.running = True
        self.word2vec = w2v.load(vocabulary_path)

    def run(self):
        # start all controllers as threads
        for controller in self.controllers:
            controller.start()

        # start voice recognition
        self.voice_recognizer.start()

        while True:
            while self.running:
                if self.voice_recognizer.triggered:
                    print 'Stop State Prediction and to force voice command'
                    for controller in self.controllers:
                        controller.pause()
                    # Find corresponding state
                    # TODO use sentiment analysis with word2vec
                    for stat in self.controllers:
                        for k in state_predictor.states.keys():
                            if state_predictor.states[k].name == voice_recognizer.instruction:
                                print 'Voice command alters state to: ' + state_predictor.states[k].name
                                state_predictor.state = state_predictor.states[k]
                                state_predictor.state.onActivation(state_predictor.getData())
                                break

                    time.sleep(5)
                    state_predictor.resume()

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True

if __name__ == '__main__':
    main_controller = MainController(StatePredictor.DummyStatePredictor(update_interval=10), VoiceClassifier())
    main_controller.start()
