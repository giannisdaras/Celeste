from __init__ import *


class State:
	"""
	This class holds state information
	"""

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


class StatePredictor(multiprocessing.Process):

	"""
		State Predictor Class. This class works like an NFA whose (predicted) next state is
		based on the previous state (like an RNN), current time data and sensor inputs. The input is fed to
		an neural network (MLP) in order to predict the probabilities of the next state and
		the index = argmax(y_prob) is selected as the next state. This class can run as a
		multiprocessing.Process allowing for running different instances of it on different CPUs
	"""

	def __init__(
			self,
			states,
			sensors,
			layout=(
				32,
				64),
			initial_state=0,
			optimizer='adam',
			update_interval=1,
			based_on_current_time=True,
			based_on_previous_states=True,
			queue=None):
		"""Constructor class arguments:
			states : a dictionary of states
			sensors : a list of sensors
			layout : MLP NN layout
			initial_state : starting state
			optimizer : model optimizer
			update_interval : update intervals
			based_on_current_time : feed current time to NN (datetime.datetime.now() objects)
			based_on_previous_states : feed previous state to NN
		"""
		super(StatePredictor, self).__init__()
		# Initializations
		self.states = states  # states as dictionary
		for k in self.states.keys():
			self.states[k].stateid = k
		self.sensors = sensors
		self.based_on_current_time = based_on_current_time
		self.based_on_previous_states = based_on_previous_states
		self.state = self.states[initial_state]
		self._stateid = multiprocessing.Value('i', self.state.stateid)
		self.start_time = time.time()
		self.layout = layout
		self._running = multiprocessing.Value('b', True)        
		self.update_interval = update_interval
		self.queue = queue
		# Input Configuration:
		# x1: Previous State
		# x2: Current Time
		# x3, xN : flattened sensor inputs
		self.num_inputs = (based_on_current_time == True) + \
			(based_on_previous_states == True)
		for s in self.sensors:
			self.num_inputs += s.output_ports
		self.num_classes = len(self.states)

		# Model configuration
		# TODO add model topology
		self.model = Sequential()
		self.model.add(Dense(layout[0], input_dim=self.num_inputs))
		self.model.add(Activation('relu'))
		self.num_train = 0
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
		""" Train neural network using data either as file or as vectors.
		(x,y) pairs should be given seperately """

		print 'Training'
		if isinstance(x, str) and isinstance(y, str):
			x = np.genfromtxt(x, delimiter=delimiter)
			y = np.genfromtxt(y, delimiter=delimiter)

		# one-hot encoding
		if not onehot:
			y = keras.utils.to_categorical(y, self.num_classes)
		self.num_train += len(x)
		x = normalize(x)
		self.model.fit(x, y, epochs=epochs, batch_size=batch_size)

	def saveWeights(self, filename='weights.h5'):
		self.model.save_weights(filename)

	def loadWeights(self, filename='weights.h5'):
		self.model.load_weights(filename)

	def __repr__(self):
		self.model.summary()

	def predict_next(self, x, verbose=False):
		""" Predct next state index = argmax (y_prob) """
		x = normalize(x)
		y_prob = self.model.predict(np.array([x]))
		index = np.argmax(y_prob)
		if verbose:
			for i in range(len(y_prob[0])):
				print 'State : {}, Probability : {}'.format(i, y_prob[0][i])
		if self.queue != None:
			self.queue.put(index)
		return index

	def getData(self):
		""" Get data from all sensors """
		x = np.array([])
		if self.based_on_current_time:
			x = np.append(x, datetime.datetime.now().hour)
		if self.based_on_previous_states:
			x = np.append(x, self.state.stateid)
		for sensor in self.sensors:
			d = sensor.getData()
			x = np.append(x, d)
		return x

	def update(self, retrain=False):
		""" Update NN """

		print 'Updating'

		x = self.getData()
		index = self.predict_next(x)

		# use softmax
		self.state = self.states[index]
		self.stateid = self.states[index].stateid
		print 'New state: {0}'.format(self.states[index].name)

		# Retrain our model
		if retrain:
			print 'Retraining'
			y = keras.utils.to_categorical(index, self.num_classes)
			self.model.train_on_batch(np.array([x]), y)
			self.num_train += 1

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

	@property
	def idle(self):
		return self.state.stateid == 0

	@idle.getter
	def idle(self):
		return self.state.stateid == 0
		
	@property
	def stateid(self):
		return self._stateid.value
	
	@stateid.getter
	def stateid(self):
		return self._stateid.value
		
	@stateid.setter
	def stateid(self, x):
		self.state = self.states[x]
		self._stateid.value = x
			
	@property
	def running(self):
		return self._running.value == True
		
	@running.setter
	def running(self, b):
		self._running.value = b
		
	@running.getter
	def running(self):
		return self._running.value == True


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
