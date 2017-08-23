from state_predictor import *
from sensors import *

# TODO Finish controller setup

class EnergySaverController(StatePredictor):

    def __init__(self):
        states = {
            0: 'do nothing',
            1 : 'close shutters',
            2 : 'open lights',
            3 : 'increase temperature',
            4 : 'decrease temperature',
        }
        sensors = []
        super(self, EnergySaverController).__init__(states, sensors)




class PlantWateringController(StatePredictor):

    def __init__(self):
        states = {
            0 : 'do nothing',
            1 : 'water'
        }
        states[1].addSubscriber(PlantWateringController.water)
        sensors = []
        super(self, PlantWateringController).__init__(states, sensors)

    @staticmethod
    def water(x):
        pass

class FridgeController(StatePredictor):

    def __init__(self):
        states = {
            0 : 'do nothing',
            1 : 'increase temperature',
            2 : 'decrease temperature'
        }
        states[1].addSubscriber(FridgeController.increase_temperature)
        states[2].addSubscriber(FridgeController.decrease_temperature)

        sensors = []
        super(self, FridgeController).__init__(states, sensors)

    @staticmethod
    def increase_temperature(x):
        pass

    @staticmethod
    def decrease_temperature(x):
        pass

class AlarmController(StatePredictor):

    def __init__(self):
        states = {
            0 : 'do nothing',
            1 : 'alarm',
            2 : 'snooze'
        }
        states[1].addSubscriber(AlarmController.alarm)
        states[2].addSubscriber(AlarmController.snooze)
        sensors = []
        super(self, AlarmController).__init__(states, sensors)

    @staticmethod
    def alarm(x):
        pass

    @staticmethod
    def snooze(x):
        pass

class PetFeederController(StatePredictor):

    def __init__(self):
        states = {
            0 : 'do nothing',
            1 : 'feed pet'
        }
        states[1].addSubscriber(PetFeederController.feed)
        sensors = [] # TODO add desired sensors
        super(self, PetFeederController).__init__(states, sensors)

    @staticmethod
    def feed(x):
        pass
