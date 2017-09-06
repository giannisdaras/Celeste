from __init__ import *


global homeName
homeName = "home"


class VoiceRecognizerModes(enum.Enum):
    IDLE = 0
    RECORD = 1
    COMMAND = 2


class VoiceRecognizer(multiprocessing.Process):
    def __init__(self, prefix=homeName, queue=None):
        super(VoiceRecognizer, self).__init__()
        self.running = True
        self.recognizer = sr.Recognizer()
        self.triggered = False  # Sets to true when it hears its name
        self._intstruction = multiprocessing.Value(c_char_p, '')
        self.prefix = prefix
        self._mode = VoiceRecognizerModes.RECORD
        self.queue = queue

    def rec(self, verbose=True):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio1 = self.recognizer.listen(source)
            try:
                message = self.recognizer.recognize_google(audio1)
                if verbose:
                    print 'message was: ' + message
                if self.mode == VoiceRecognizerModes.COMMAND and self.prefix in message:
                    self.triggered = True
                    text = message[message.index(
                        self.prefix) + len(self.prefix) + 1:]
                    self.instruction = text
                elif self.mode == VoiceRecognizerModes.RECORD:
                    self.triggered = True
                    self.instruction = message
                if self.queue is not None:
                    self.queue.put(self.instruction)
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
    def instruction(self):
        return self._intstruction.value

    @instruction.setter
    def instruction(self, data):
        self._intstruction.value = data

    @instruction.getter
    def instruction(self):
        return self._intstruction.value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        assert(mode == VoiceRecognizerModes.RECORD or mode ==
               VoiceRecognizerModes.COMMAND)
        self._mode = mode

    def clear_record_cache(self):
        if self.queue is None:
            return
        while not self.queue.empty():
            self.queue.get()


class VoiceCommandClassifier(VoiceRecognizer):

    def __init__(self, prefix=homeName, queue=None):
        super(VoiceCommandClassifier, self).__init__(
            prefix=prefix, queue=queue)
        self.bayesian_classifier = Pipeline([('vect', CountVectorizer()),
                                             ('tfidf', TfidfTransformer(
                                                 use_idf=False)),
                                             ('clf', MultinomialNB()), ])

    def train_classifier(self, x, y):
        self.bayesian_classifier.fit(x, y)
