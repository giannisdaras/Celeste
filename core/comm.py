from __init__ import *


class BoardNotFoundException(Exception):

    def __init__(self):
        msg = 'board not found'
        super(BoardNotFoundException, self).__init__(msg)


def get_board(num_tries=10):
    for i in range(num_tries):
        try:
            board = PyMata('/dev/ttyACM{0}'.format(i), verbose=False)
            return board
        except:
            continue
    raise BoardNotFoundException()

class Sensor(object):

    def __init__(self, name, output_ports):
        self.name = name
        self.output_ports = output_ports

    def getData(self):
        return None

    def __len__(self):
        return self.output_ports


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

    def __init__(self, name, board, input_pins=[]):
        super(ArduinoDigitalSensor, self).__init__(name, output_ports=len(input_pins))
        self.board = board
        self.input_pins = input_pins
        for p in input_pins:
            self.board.set_pin_mode(p, board.INPUT, board.DIGITAL)

    def getData(self):
        try:
            self.board.capability_query()
            x = np.array([])
            response = self.board.get_analog_response_table()
            for p in self.input_pins:
                x = np.append(x, response[p][0])
            return x
        except:
            return None

    def writeData(self, x):
        assert(len(x) == len(self.input_pins))
        try:
            for i in range(len(self.input_pins)):
                self.board.digital_write(self.input_pins[i], x[i])
            return True
        except:
            return False


class ArduinoAnalogSensor(Sensor):

    def __init__(self, name, board, input_pins=[]):
        super(ArduinoAnalogSensor, self).__init__(name, output_ports=len(input_pins))
        self.board = board
        self.input_pins = input_pins
        for p in input_pins:
            self.board.set_pin_mode(p, board.INPUT, board.ANALOG)

    def getData(self):
        try:
            self.board.capability_query()
            x = np.array([])
            response = self.board.get_analog_response_table()

            for p in self.input_pins:
                x = np.append(x, response[p][0])
            return x
        except:
            return None

    def writeData(self, x):
        assert(len(x) == len(self.input_pins))
        try:
            for i in range(len(self.input_pins)):
                self.board.analog_write(self.input_pins[i], x[i])
            return True
        except:
            return False

class LEDArray(ArduinoDigitalSensor):

    def __init__(self, name, board, input_pins=[]):
        super(LEDArray, self).__init__(
            name, len(input_pins), board, input_pins)

        for pin in input_pins:
            self.board.set_pin_mode(pin, board.OUTPUT, board.DIGITAL)

class CommTestCases(unittest.TestCase):

    def setUp(self):
        self.board = get_board()

    def testLEDArray(self):
        ledarray = LEDArray('larray', self.board, input_pins=[13])
        ledarray.writeData([1])
        print ledarray.getData()

    def testLightSensor(self):
        ls = ArduinoAnalogSensor('light', self.board, input_pins=[0])
        for i in range(10):
            print ls.getData()


if __name__ == '__main__':
    unittest.main()
