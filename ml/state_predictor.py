from __init__ import *

def softmax(y):
    z = np.exp(y)
    return z / np.sum(z)


class State:

    def __init__(self, name, stateid):
        self.name = name
        self.data = np.array([])
        self.stateid = stateid
        self.subscribers = [self.nameSub]

    def addData(self, x):
        np.append(self.data, x)

    def __le__(self, other):
        return self._likelihood < other._likelihood

    def onActivation(self, x):
        for f in self.subscribers:
            f(x)

    def addSubscriber(self, sub):
        self.subscribers.append(sub)

    def nameSub(self, x):
        print 'Subscriber called for ' + self.name


class Sensor:

    def __init__(self, name, output_ports):
        self.name = name
        self.output_ports = output_ports

    def getData(self):
        return None


class DummySensor(Sensor):

    def __init__(self, name, output_ports, lower, upper):
        # super(DummySensor, self).__init__(name, output_ports)
        self.name, self.output_ports = name, output_ports
        self.lower, self.upper = lower, upper

    def getData(self):
        return np.array(self.output_ports *
                        [np.random.randint(self.lower, self.upper)])


class Camera(Sensor):

    def __init__(self, name, index):
        self.cam = cv2.VideoCapture(index)
        ret, frame = self.cam.read()
        frame = frame.flatten()
        super(Camera, self).__init__(name, frame.shape[0])

    def getData(self, grayscale=True):
        ret, frame = self.cam.read()
        if grayscale:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return frame

    def __del__(self):
        self.cam.release()


class StatePredictor(threading.Thread):

    def __init__(
            self,
            states,
            sensors,
            layout=(
                32,
                64),
            initial_state=1,
            optimizer='adam',
            update_interval=1):
        super(StatePredictor, self).__init__()
        # Initializations
        self.states = states  # states as dictionary
        for k in self.states.keys():
            self.states[k].stateid = k
        self.sensors = sensors
        self.state = self.states[initial_state]
        self.start_time = time.time()
        self.layout = layout
        self.running = True
        self.update_interval = update_interval
        # Input Configuration:
        # x1: Previous State
        # x2: Current Time
        # x3, xN : flattened sensor inputs
        self.num_inputs = 2
        for s in self.sensors:
            self.num_inputs += s.output_ports

        self.num_classes = len(self.states)

        # Model configuration
        # TODO add model topology
        self.model = Sequential()
        self.model.add(Dense(layout[0], input_dim=self.num_inputs))
        self.model.add(Activation('relu'))

        for i in range(1, len(layout)):
            self.model.add(Dense(layout[i]))
            self.model.add(Activation('relu'))

        # Outputs
        # y1, y2, ym : Next state probabilities
        self.model.add(Dense(self.num_classes, activation='sigmoid'))

        self.model.compile(loss='categorical_crossentropy',
                           optimizer=optimizer,
                           metrics=['accuracy'])

    def train(
            self,
            x,
            y,
            onehot=False,
            epochs=30,
            batch_size=128,
            delimiter=' '):
        print 'Training'
        if isinstance(x, str) and isinstance(y, str):
            x = np.genfromtxt(x, delimiter=delimiter)
            y = np.genfromtxt(y, delimiter=delimiter)

        # one-hot encoding
        if not onehot:
            y = keras.utils.to_categorical(y, self.num_classes)

        self.model.fit(x, y, epochs=epochs, batch_size=batch_size)

    def saveWeights(self, filename='weights.h5'):
        self.model.save_weights(filename)

    def loadWeights(self, filename='weights.h5'):
        self.model.load_weights(filename)

    def __repr__(self):
        self.model.summary()

    def predict_next(self, x, verbose=True):
        y_prob = self.model.predict(np.array([x]))
        index = np.argmax(y_prob)
        if verbose:
            for i in range(len(y_prob[0])):
                print 'State : {}, Probability : {}'.format(i, y_prob[0][i])
        return index

    def getData(self):
        dt = datetime.datetime.now().hour
        x = np.array([dt, self.state.stateid])
        for sensor in self.sensors:
            d = sensor.getData()
            x = np.append(x, d)
        return x

    def update(self, retrain=True):
        print 'Updating'

        x = self.getData()
        index = self.predict_next(x)

        # use softmax
        self.state = self.states[index]
        print 'New state: {0}'.format(self.states[index].name)

        # Retrain our model
        if retrain:
            print 'Retraining'
            y = keras.utils.to_categorical(index, self.num_classes)
            self.model.train_on_batch(np.array([x]), y)

        self.state.onActivation(x)

    def evaluate(self, x_test, y_test, delimiter=' '):
        if isinstance(x_test, str) and isinstance(y_test, str):
            x_test = np.genfromtxt(x_test, delimiter=delimiter)
            y_test = np.genfromtxt(y_test, delimiter=delimiter)

        self.scores = self.model.evaluate(x_test, y_test)
        return self.scores

    def run(self):
        while True:
            while self.running:
                self.update()
                time.sleep(self.update_interval)

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True

    @staticmethod
    def DummyStatePredictor(update_interval=1):
        sensors = [
            DummySensor('number_of_people', 1, 0, 20),
            DummySensor('mood', 1, 0, 10),
            DummySensor('light', 1, 0, 255),
            DummySensor('temperature', 1, 10, 40)
        ]

        states = {
            0: State('do nothing', 0),
            1: State('raise temperature', 1),
            2: State('decrease temperature', 2),
            3: State('turn on music', 3),
            4: State('close shutters', 4),
        }
        state_predictor = StatePredictor(states, sensors, update_interval=update_interval)
        return state_predictor

# Testcase


def test():
    state_predictor = StatePredictor.DummyStatePredictor()
    state_predictor.start()
    time.sleep(5)
    print 'Thread paused'
    state_predictor.pause()
    time.sleep(5)
    print 'Thread continues'
    state_predictor.resume()

if __name__ == '__main__':
    test()
