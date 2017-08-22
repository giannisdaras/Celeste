# Controller
from ml.state_predictor import StatePredictor
from ml.voice import VoiceClassifier
import time

if __name__ == '__main__':
    state_predictor = StatePredictor.DummyStatePredictor(update_interval=10)
    voice_recognizer = VoiceClassifier()

    state_predictor.start()
    voice_recognizer.start()

    while True:
        if voice_classifier.triggered:
            print 'Stop state prediction'
            state_predictor.pause()
            time.sleep(5)
            print 'Resuming state prediction'
            state_predictor.resume()
