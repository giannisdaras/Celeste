#!/usr/bin/env python

# Controller
from core.controllers import *
from core.voice import VoiceRecognizer
import time
import threading
import psycopg2
import sys
import core.minifig
try:
	from core.comm import *
except:
	pass

#Constants
LEARNING_RATE = 0.2

class MainController(threading.Thread):
	''' This class holds main controller that is responsible for synchronizing the
	rest of the controllers. Due to GIL it is obliged to be a threading.Thread '''

	def __init__(self, controllers = [], update_interval=10):
		self.update_interval = update_interval

		'''Threading related stuff'''
		super(MainController, self).__init__()
		try:
			self.board_manager = BoardManager()
			self.board = board_manager.Board()
		except:
			pass
		self.lock = self.manager.Lock()
		self.controllers = controllers
		self.running = True
		self.kill=False






		''' Establish connection with database'''
		try:
			self.conn = psycopg2.connect(
				"dbname='Celeste' user='postgres' host='localhost' password='1234'")
		except:
			raise Exception('Could not find database. Exiting now')
			sys.exit(1)
		''' ------------------------ '''

		self.cur = self.conn.cursor()
		self.cur.execute('select * from settings')
		self.config = int(self.cur.fetchall()[0][2])
		self.q = multiprocessing.Queue()
		self.q.put(self.config)
		self.names=next(os.walk('./haar/positive_images'))[1]
		self.minifig_detector = core.minifig.initialize_from_directory(names=self.names, update_interval=update_interval, source_dir='./haar', new_weights=False)
		if (self.config):
			for i in range(len(self.names)):
				query="insert into people (id,name,gender) values ({},'{}','male')".format(i,self.names[i])
				self.cur.execute(query)
			self.conn.commit()
		self.voice=VoiceRecognizer(self.q)


		# Put data into table
		while not self.q.empty():
			self.cur.execute(self.q.get())
			self.conn.commit()

		# Create minifig detector
		self.cur.execute('select name, rooms from people')
		response = self.cur.fetchall()
		self.names = map(lambda x : x[0], response)
		self.rooms_auth = self.manager.dict(zip(self.names, map(lambda x : x[1], response)))


		self.minifig_detector = core.minifig.initialize_from_directory(names=self.names, update_interval=update_interval, source_dir='./haar', new_weights=False)

		# Basic Controller Setup

		self.controllers.append(AuthorizationController(minifig_detector=self.minifig_detector, rooms_auth=self.rooms_auth, update_interval=self.update_interval))



		self.start()


	def changeState(self, i, k, wait_interval=0.5):
		self.controllers[i].stateid = k
		#self.controllers[i].state = self.controllers[i].states[k]
		self.controllers[i].state.onActivation(self.controllers[i].getData())
		time.sleep(wait_interval)
		y = keras.utils.to_categorical(k, self.constrollers[i].num_classes)

		n = int(LEARNING_RATE * self.controllers[i].num_train)
		x = self.constrollers[i].getData()
		for i in range(n):
			self.constrollers[i].model.train_on_batch(np.array([x]), y)
		self.controllers[i].num_train += n
		self.controllers[i].resume()

	def joinAll(self):
		for controller in self.controllers:
			controller.join()

	def shutDown(self):
		try:
			for controller in self.controllers:
				controller.terminate()
			self.joinAll()
			self.pause()
			self.kill = True
			super(MainController, self).join()
			print 'Terminated everything'
			return True
		except:
			return False

	def classify_command(self, query):
		"""Classifies commands by edit distance"""
		controller_min = -1
		state_min = -1
		min_edit_distance = -1

		for i, controller in enumerate(self.controllers):
			for j, state in enumerate(constroller.states):
				d = edit_distance(query, state.name)
				if d <= min_edit_distance or min_edit_distance == -1:
					min_edit_distance = d
					controller_min = i
					state_min = j
		self.changeState(i,j)

	def run(self):
		# start all controllers as threads
		for controller in self.controllers:
			controller.start()

		self.minifig_detector.start()

		# main thread body
		while True:
			while self.running:
				while not self.q.empty():
					try:
						query = self.q.get()
						self.classify_command(query)
					except:
						break

			if self.kill:
				return

	def pause(self):
		self.running = False

	def resume(self):
		self.running = True

if __name__ == '__main__':
	main_controller = MainController(
		[DummyController(update_interval=2)])
	# time.sleep(3)
	# main_controller.shutDown()
