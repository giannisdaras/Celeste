from __init__ import *

def get_board(num_tries=10):
    for i in range(num_tries):
        try:
            board = PyMata('/dev/ttyACM{0}'.format(i))
            return board
        except:
            continue
    return None

# Sensing


class Sensor:

    def __init__(self, name, output_ports):
        self.name = name
        self.output_ports = output_ports

    def getData(self):
        return None


class DummySensor(Sensor):
    """ Sensor that outputs random data """

    def __init__(self, name, output_ports, lower, upper):
        super(DummySensor, self).__init__(name, output_ports)
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


class ArduinoPin:

    def __init__(self, pin, mode, pintype):
        # TODO add property setters and getters
        self.pin = pin
        self.mode = mode
        self.pintype = pintype


class ArduinoSensor(Sensor):

    def __init__(self, name, output_ports, board, input_pins=[]):
        super(ArduinoSensor, self).__init__(name, output_ports)
        self.board = board
        self.input_pins = input_pins

        # setup board
        for pin in input_pins:
            self.board.set_pin_mode(pin.pin, self.board.INPUT if pin.mode == 'INPUT' else self.board.PWM,
                                    self.board.DIGITAL if pin.pintype == 'DIGITAL' else self.board.ANALOG)

    def getData(self):
        x = np.array([])
        for pin in self.input_pins:
            x = np.append(x, self.board.analog_read(pin.pin))
        return x

# Enums for Arduino
# TODO Add desired sensors

class LEDArray(ArduinoSensor):

    def __init__(self, name, board, input_pins=[]):
        super(LEDArray, self).__init__(name, len(input_pins), board, input_pins)

        for pin in input_pins:
            self.board.set_pin_mode(pin, board.OUTPUT, board.DIGITAL)

    def getData(self):
        self.board.capability_query()
        x = np.array([])
        response = self.board.get_digital_response_table()
        for x_ in response:
            x = np.append(x, [x_[0]])
        return x

    def writeLeds(self, leds):
        for i in range(len(self.input_pins)):
            self.board.digital_write(self.input_pins[i], leds[i])

class LightSensor(ArduinoSensor):
    pass

class TemperatureSensor(ArduinoSensor):
    pass

class ArduinoSensors:
    pass


class ArduinoOutputs:
    pass

if __name__ == '__main__':
    ledarray = LEDArray('larray', get_board(), input_pins=[13])
    ledarray.writeLeds([1])
    print ledarray.getData()
