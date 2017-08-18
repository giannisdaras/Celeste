from __init__ import *

def softmax(y):
	z = np.exp(y)
	return z / np.sum(z)

class State:

	def __init__(self, name, stateid):
		self.name = name
		self.data = np.array([])
		self.stateid = stateid
		self.subscribers = []

	def addData(x):
		np.append(self.data, x)

	def __le__(self, other):
		return self._likelihood < other._likelihood

	def onActivation(x):
		for f in self.subscribers:
			f(x)

	def addSubscriber(self, sub):
		self.subscribers.append(sub)

class Sensor:

	def __init__(self, name, output_ports):
		self.name = namedtuple
		self.output_ports = output_ports

	def getData(self):
		return np.random.rand(1, self.output_ports)

def Camera(Sensor):

	def __init__(self, name, index):
		self.cam = cv2.VideoCapture(index)
		ret, frame = self.cam.read()
		frame = frame.flatten()
		super(Camera, self).__init__(name, frame.shape[0])

	def getData(self, grayscale=True):
		ret, frame = self.cam.read()
		if grayscale:
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
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
		self.state = State('initial', -1)
		self.start_time = time.time()
		# Input Configuration:
		# x1: Previous State
		# x2: Current Time
		# x3, xN : flattened sensor inputs
		self.num_inputs = 2
		for s in self.states:
			self.num_inputs += s.output_ports

		self.num_classes = len(self.states)

		#Model configuration
		# TODO add model topology
		self.model = Sequential()
		self.model.add(Dense(32, input_dim=self.num_inputs, activation='relu'))


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
		self.model.loadWeights(filename)

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

"""Unittesting class
	Sample arrangement with 3 sensors outputing random data
"""
class StatePredictorUnittest(unittest.TestCase):

	def setUp(self):
		self.sensors = [
		Sensor('sensor1', 1),
		Sensor('sensor2', 255),
		Sensor('sensor3', 64)
		]

		self.states = {
		1 : State('cook', 1)
		2 : State('set_table', 2)
		3 : State('enable_thermostat', 3)
		4 : State('disable_thermostat', 4)
		}

		self.state_predictor = StatePredictor(states, sensors)

	def test_trainnetwork(self):
		# TODO complete unittesting
		pass

	def tearDown(self):
		pass
