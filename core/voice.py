from __init__ import *

global homeName
homeName = "home"


class VoiceRecognizerModes(enum.Enum):
    RECORD = 0
    COMMAND = 1


class VoiceRecognizer(multiprocessing.Process):
    def __init__(self, prefix=homeName):
        super(VoiceRecognizer, self).__init__()
        self.running = True
        self.recognizer = sr.Recognizer()
        self.triggered = False  # Sets to true when it hears its name
        self.instruction = ''  # holds last instruction as string
        self.message = ''
        self.prefix = prefix
        self._mode = VoiceRecognizerModes.RECORD

    def rec(self, verbose=True):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio1 = self.recognizer.listen(source)
            try:
                message = self.recognizer.recognize_google(audio1)
                print 'message was: ' + message
                if self.mode == VoiceRecognizerModes.COMMAND and self.prefix in message:
                    self.triggered = True
                    text = message[message.index(
                        self.prefix) + len(self.prefix) + 1:]
                    self.instruction = text
                elif self.mode == VoiceRecognizerModes.RECORD:
                    self.instruction = message
            except sr.UnknownValueError:
                print('Untracked')
            finally:
                time.sleep(1)
                self.triggered = False

    def run(self):
        while True:
            while self.running:
                self.rec()

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        assert(mode == VoiceRecognizerModes.RECORD or mode ==
               VoiceRecognizerModes.COMMAND)
        self._mode = mode

# TODO Add classification class with bayesian classifier


class VoiceCommandClassifier(VoiceRecognizer):
    pass


class VoiceRecognizerUnittest(unittest.TestCase):

    def test_voice_recognizer(self):
        voice_recognizer = VoiceRecognizer()
        voice_recognizer.start()
        time.sleep(20)
        voice_recognizer.terminate()
        voice_recognizer.join()


if __name__ == '__main__':
    unittest.main()
