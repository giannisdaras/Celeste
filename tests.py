# Holds all tests
import unittest
from core.minifig import *
from core.comm import *
from main import *
from core.voice import *


class VoiceRecognizerUnittest(unittest.TestCase):

    def test_voice_recognizer(self):
        voice_recognizer = VoiceRecognizer()
        voice_recognizer.start()
        time.sleep(20)
        voice_recognizer.terminate()
        voice_recognizer.join()


class MinifigDetectorUnittest(unittest.TestCase):

    def setUp(self):
        cascade = '/usr/local/lib/node_modules/opencv/data/haarcascade_frontalface_alt2.xml'
        john_doe = Minifig('John Doe')
        sigmund_freud = Minifig('Sigmund Freud')
        self.md = MinifigDetector(
            [john_doe, sigmund_freud], update_interval=2, cascade_classifier=cascade)

    def test_with_random_data(self):
        self.md.start()
        time.sleep(10)
        self.md.terminate()
        self.md.join()


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


class MainControllerUnittest(unittest.TestCase):

    def setUp(self):
        self.main_controller = MainController(
            [DummyController(update_interval=2)])

    def test_dummy(self):
        self.main_controller.start()
        time.sleep(10)
        self.main_controller.shutDown()


if __name__ == '__main__':
    unittest.main()
