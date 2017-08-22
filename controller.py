# Controller
from ml.state_predictor import StatePredictor
from ml.voice import VoiceClassifier
import time
import threading

class MainController(threading.Thread):

    def __init__(self, state_predictor, voice_recognizer):
        threading.Thread.__init__(self)
        self.state_predictor = state_predictor
        self.voice_recognizer = voice_recognizer
        self.running = True

    def run(self):
        self.state_predictor.start()
        self.voice_recognizer.start()
        while True:
            while self.running:
                if self.voice_recognizer.triggered:
                    print 'Stop State Prediction and to force voice command'
                    state_predictor.pause()
                    # Find corresponding state
                    # TODO use sentiment analysis
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
