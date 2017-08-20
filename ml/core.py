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

	def addData(x):
		np.append(self.data, x)

	def __le__(self, other):
		return self._likelihood < other._likelihood

	def onActivation(x):
		for f in self.subscribers:
			f(x)

	def addSubscriber(self, sub):
		self.subscribers.append(sub)

	def nameSub(self ,x):
		print self.name

class Sensor:

	def __init__(self, name, output_ports):
		self.name = name
		self.output_ports = output_ports

	def getData(self):
		return None

class DummySensor(Sensor):

	def __init__(self, name, output_ports, lower, upper):
		#super(DummySensor, self).__init__(name, output_ports)
		self.name, self.output_ports = name, output_ports
		self.lower, self.upper = lower, upper

	def getData(self):
		return np.array(self.output_ports * [np.random.randint(self.lower, self.upper)])

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

class StatePredictor:

	def __init__(self, states, sensors, optimizer='adam'):
		# Initializations
		self.states = states #states as dictionary
		for k in self.states.keys():
			self.states[k].stateid = k
		self.sensors = sensors
		self.states[0] = State('initial', 0)
		self.state = self.states[0]
		self.start_time = time.time()
		# Input Configuration:
		# x1: Previous State
		# x2: Current Time
		# x3, xN : flattened sensor inputs
		self.num_inputs = 2
		for s in self.sensors:
			self.num_inputs += s.output_ports

		self.num_classes = len(self.states)

		#Model configuration
		# TODO add model topology
		self.model = Sequential()
		self.model.add(Dense(16, input_dim=self.num_inputs, activation='relu'))

		self.model.add(Dense(32))
		self.model.add(Activation('relu'))

		# Outputs
		# y1, y2, ym : Next state probabilities
		self.model.add(Dense(self.num_classes, activation='sigmoid'))


		self.model.compile(loss='categorical_crossentropy',
		optimizer=optimizer,
		metrics=['accuracy'])

	def train(self, x, y, onehot=False, epochs=30, batch_size=128, delimiter=' '):
		if type(x) == str and type(y) == str:
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

	def update(self):
		dt = time.time() - self.start_time
		x = np.array([dt, self.state.stateid])

		for sensor in self.sensors:
			np.append(x, sensor.getData().flatten())

		y_hat = self.model.predict(x)
		#use softmax
		# y_hat = softmax(self.model.predict(x))
		index = np.argmax(y_hat)
		self.state = self.states[index]
		print 'New state: {0}'.format(self.states[index])

		self.state.OnActivation(x)

	def evaluate(self, x_test, y_test, delimiter=' '):
		if type(x_test) == str and type(y_test) == str:
			x_test = np.genfromtxt(x_test, delimiter=delimiter)
			y_test = np.genfromtxt(y_test, delimiter=delimiter)

		self.scores = self.model.evaluate(x_test, y_test)
		return self.scores

class StatePredictorThread(threading.Thread):

	def __init__(self, predictor, update_interval=1):
		super(StatePredictorThread, self).__init__()
		self.predictor = predictor
		self.update_interval = update_interval

	def run(self):
		while True:
			self.predictor.update()
			time.sleep(self.update_interval)

# Unittesting
def test():
	sensors = [
		DummySensor('number_of_people', 1, 0, 20),
		DummySensor('mood', 1, 0, 10),
		DummySensor('light', 1, 0, 255),
		DummySensor('temperature', 1, 10, 40)
	]

	states = {
		1 : State('Do Nothing', 1),
		2 : State('Raise temperature', 2),
		3 : State('Decrease temperature', 3),
		4 : State('Turn on music', 4),
		5 : State('Close shutters', 5),
	}

	state_predictor = StatePredictor(states, sensors)
	state_predictor.train('train_data_x.csv', 'train_data_y.csv')
	state_predictor.saveWeights()

	state_predictor_thread = StatePredictorThread(predictor=state_predictor, update_interval=update_interval)
	state_predictor_thread.start()
test()
