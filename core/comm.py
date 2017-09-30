from __init__ import *


class BoardNotFoundException(Exception):

	def __init__(self):
		msg = 'board not found'
		super(BoardNotFoundException, self).__init__(msg)


class Board(Arduino):
	def __init__(self, num_tries=10):
		for i in range(num_tries):
			try:
				super(Board, self).__init__('/dev/ttyACM{0}'.format(i))
				return
			except:
				continue
		raise BoardNotFoundException()
		self.it = util.Iterator(self)
		
		
class BoardManager(BaseManager):
		
		def __init__(self):
			super(BoardManager, self).__init__()
			super(BoardManager, self).register('Board', Board)
			super(BoardManager, self).start()
	
class Sensor(object):

	def __init__(self, name, output_ports):
		self.name = name
		self.output_ports = output_ports

	def getData(self):
		return None

	def __len__(self):
		return self.output_ports

class Servo(object):
	
	def __init__(self, servo_pin, board):
		self.board = board
		self.pin = self.board.get_pin('d:{}:s'.format(servo_pin))
		self.pin.write(0)
		
	def rotate(self, x):
		self.pin.write(x)
		self.pin.write(0)
		
class DummySensor(Sensor):
	""" Sensor that outputs random data """

	def __init__(self, name, output_ports, lower, upper):
		super(DummySensor, self).__init__(name, output_ports)
		self.lower, self.upper = lower, upper

	def getData(self):
		return np.array(self.output_ports *
						[np.random.randint(self.lower, self.upper)])


class Camera(Sensor):

	def __init__(self, name='cam', index=0):
		self.cam = cv2.VideoCapture(index)
		ret, frame = self.cam.read()
		super(Camera, self).__init__(
			name=name, output_ports=frame.shape[0] * frame.shape[1])

	def getData(self, grayscale=True):
		ret, frame = self.cam.read()
		if grayscale:
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		return frame

	def __del__(self):
		self.cam.release()

class ArduinoDigitalSensor(Sensor):
	pins=[]
	def __init__(self, name, board, input_pins=[]):
		super(ArduinoDigitalSensor, self).__init__(name, output_ports=len(input_pins))
		self.board = board
		self.input_pins = input_pins
		for p in input_pins:
			self.pins.append(self.board.get_pin('d:%d:i' % p))
			#self.board.set_pin_mode(p, board.INPUT, board.DIGITAL)


	def getData(self):

			 
		try:
			x = np.array([])
			for p in self.pins:
				x = np.append(x,p.read())
			return x
		except:
			return None
	def  writeData(self, x):
	   assert(len(x)==len(self.input_pins))
	   for i in range(len(self.input_pins)):
		  self.board.digital[self.input_pins[i]].write(x[i])
		  





class LEDArray(ArduinoDigitalSensor):
	pins=[]
	def __init__(self, name, board, input_pins=[]):
		self.board=board
		self.input_pins=input_pins
		for p in input_pins:
			self.pins.append(board.get_pin('d:%d:o' %p))


class ArduinoAnalogSensor(Sensor):
	pins=[]
	def __init__(self, name, board, input_pins=[]):
		self.board = board
		self.input_pins = input_pins
		for p in input_pins:
			self.pins.append(self.board.get_pin('a:%d:i' % p))
	

	def getData(self):
		try:
			x = np.array([])
			for p in self.pins:
				x = np.append(x, p.read())
			return x
		except:
			return None

	def writeData(self, x):
		assert(len(x) == len(self.input_pins))
		try:
			for i in range(len(self.input_pins)):
				self.board.analog[self.input_pins[i]].write(x[i])
			return True
		except:
			return False            
