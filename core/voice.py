from __init__ import *


global homeName
homeName = "home"


class VoiceRecognizer(multiprocessing.Process):
    def __init__(self,q,prefix=homeName):
        super(VoiceRecognizer, self).__init__()
        self.recognizer = sr.Recognizer()
        self.q=q
        self.config=self.q.get()
        self.running=True
        if (self.config==1):
            self.configure()
        else:
            self.start()

    def rec(self):
        if (self.running==True):
            with sr.Microphone() as source:
                print('Here')
                self.recognizer.adjust_for_ambient_noise(source)
                audio1 = self.recognizer.listen(source)
                try:
                    message = self.recognizer.recognize_google(audio1)
                    print(message)
                    if ('Celeste' in message):
                        self.running=False
                        self.talk('You said {0}'.format(message))
                except sr.UnknownValueError:
                    message='Untracked'
                finally:
                    time.sleep(1)

    def recordOnce(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while(True):
                audio1 = self.recognizer.listen(source)
                try:
                    message = self.recognizer.recognize_google(audio1)
                    break
                except sr.UnknownValueError:
                    self.talk('Please repeat')
        return(message)
                    



    def run(self):
        while True:
            self.rec()

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True

    def talkAndWait(self,text):
        f=Popen("google_speech -l en '{0}'".format(text), shell=True)
        f.wait()
        del f
        return(self.recordOnce())
    def talk(self,text):
        f=Popen("google_speech -l en '{0}'".format(text), shell=True)
        f.wait()
        del f
        self.running=True



    def configure(self):
        print(self.talkAndWait('Hello user, tell me your name'))
        print(self.talkAndWait('Nice name. What is your favorite color?'))
        self.run()




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
