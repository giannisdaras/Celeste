from state_predictor import *
from comm import *

class AuthorizationController(StatePredictor):
	
	def __init__(self, minifig_detector, rooms_auth, update_interval = 10):
		self.minifig_detector = minifig_detector
		self.rooms_auth = rooms_auth
		
		self.rooms = []
		for r in self.rooms_auth.values():
			self.rooms.extend(r)
		self.rooms = list(set(self.rooms))
		self.rooms_auth_status = {}
		
		for r in self.rooms:
			self.rooms_auth_status[r] = False
		
		states = {
			0 : State('do nothing', 0),
			1 : State('open door', 1),
			2 : State('close door', 2)	
		}
		self.update_interval = update_interval
		super(AuthorizationController, self).__init__(states=states, sensors=[], update_interval=update_interval)

	def update(self):
		
		for lbl in self.minifig_detector.class_labels:
			if self.minifig_detector.status[lbl] >= 1:
				for r in self.rooms[lbl]:
					self.rooms_auth_status[r] = True	
		
		for r in self.rooms:
			if self.rooms_auth_status[r] == True:
				self.open_door(r)
			else:
				self.close_door(r)
		
		self.reset_auth()
			
	def reset_auth(self):
		for r in self.rooms:
			self.rooms_auth_status[r] = False	
		
	def open_door(self, x):
		pass
		
	def close_door(self, x):
		pass
		
class EnergySaverController(StatePredictor):
	
	def __init__(self, update_interval):		
		states = {
			0: 'do nothing',
			1 : 'close shutters',
			2 : 'open lights',
			3 : 'increase temperature',
			4 : 'decrease temperature',
		}
		sensors = []
		super(EnergySaverController, self).__init__(states, sensors)
		
		
	
# Controllers based on state predictors
# Example controlller
class DummyController(StatePredictor):

	def __init__(self, update_interval = 1):
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
		super(DummyController, self).__init__(states, sensors, update_interval=update_interval)

class PlantWateringController(StatePredictor):

	def __init__(self):
		states = {
			0 : 'do nothing',
			1 : 'water'
		}
		states[1].addSubscriber(PlantWateringController.water)
		sensors = []
		super(PlantWateringController, self).__init__(states, sensors)

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
		super(FridgeController, self).__init__(states, sensors)

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
		super(AlarmController, self).__init__(states, sensors)

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
		super(PetFeederController, self).__init__(states, sensors)

	@staticmethod
	def feed(x):
		pass

class HologramController(StatePredictor):
	def __init__(self,hologramQuery,update_interval=1):
		states = {
		0:State('do nothing',0),
		1:State('update hologram',1)
		}
		sensors=[]
		super(HologramController, self).__init__(states, sensors, update_interval=update_interval)
		states[0].addSubscriber(HologramController.updateHologram)
	
	@staticmethod
	def updateHologram(x):

