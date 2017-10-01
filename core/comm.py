from __init__ import *
import glob

class BoardNotFoundException(Exception):

	def __init__(self):
		msg = 'board not found'
		super(BoardNotFoundException, self).__init__(msg)


class Board(threading.Thread):
	
	def __init__(self, board_queue = multiprocessing.Queue()):
		
		serial_ports = glob.glob('/dev/ttyACM*')
		
		self.brd = Arduino(serial_ports[0])
		print 'Board found at {0}'.format(serial_ports[0])
		self.board_queue = board_queue
		self.components = {}
		self.components['servo1'] = Servo(servo_pin = 9, board = self.brd)
		self.components['servo2'] = Servo(servo_pin = 10, board = self.brd)		
		self.components['servo3'] = Servo(servo_pin = 11, board = self.brd)
		self.components['ledarray'] = LEDArray(input_pins = [13, 12], board = self.brd)
		self.components['photoresistor'] = ArduinoAnalogSensor(input_pins = [0], board = self.brd)

		super(Board, self).__init__()

	def run(self):
		while True:
			if (not self.board_queue.empty()):
				instruction=self.board_queue.get()
				if ('servo1' in instruction):
					self.components['servo1'].rotate(instruction[1])
				elif ('servo2' in instruction):
					self.components['servo2'].rotate(instruction[1])
				elif ('servo3' in instruction):
					self.components['servo3'].rotate(instruction[1])
				elif ('ledarray' in instruction):
						self.components['ledarray'].writeData(instruction[1])
	
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

class Camera(Sensor):

	def __init__(self, name='cam', index=0):
		self.cam = cv2.VideoCapture(index)
		ret, frame = self.cam.read()
		try:
			super(Camera, self).__init__(
				name=name, output_ports=frame.shape[0] * frame.shape[1])
		except:
			print("Exception here!")
			super(Camera, self).__init__(
				name=name, output_ports=640 * 480)
			

	def getData(self, grayscale=True):
		ret, frame = self.cam.read()
		if grayscale:
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		return frame

	def __del__(self):
		self.cam.release()

class ArduinoDigitalSensor(Sensor):
	def __init__(self, board, input_pins=[]):
		super(ArduinoDigitalSensor, self).__init__(name, output_ports=len(input_pins))
		self.board = board
		self.pins = []
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

	def __init__(self, board, input_pins=[]):
		self.board=board
		self.input_pins=input_pins
		self.pins = []
		for p in input_pins:
			self.pins.append(board.get_pin('d:%d:o' %p))


class ArduinoAnalogSensor(Sensor):

	def __init__(self,  board, input_pins=[]):
		self.board = board
		self.input_pins = input_pins
		self.pins = []
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
