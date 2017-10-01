from state_predictor import *
from comm import *

class AuthorizationController(StatePredictor):
	
	def __init__(self, minifig_detector, rooms_auth, board_queue, update_interval = 10):
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
			0 : State('open door', 0),
			1 : State('close door', 1)	
		}
		self.update_interval = update_interval
		super(AuthorizationController, self).__init__(states=states, sensors=[], update_interval=update_interval, board_queue = board_queue)

	def update(self):
		
		for lbl in self.minifig_detector._class_labels:
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
		self.board_queue.put(['servo{}'.format(x), 90])
	
	def close_door(self, x):
		self.board_queue.put(['servo{}'.format(x), 90])
		
class EntranceController(StatePredictor):
	
	def __init__(self, minifig_detector, board_queue, update_interval=10):
		self.minifig_detector = minifig_detector
		self.entrance_id = entrance_id
		states = {
			0 : State('do nothing', 0),
			1 : State('open entrance', 1),
			2 : State('close entrance', 2)
		}
		states[1].addSubscriber(self.open_door)
		states[2].addSubscriber(self.close_door)
		super(EntranceController, self).__init__(states=states, sensors = [], board_queue = board_queue,  update_interval = update_interval)
		
	def update(self):
		
		if self.minifig_detector.number_of_people > 0:
			self.open_door(self.entrance_id)
			time.sleep(update_interval)
			self.close_door(self.entrance_id)
	
	def open_door(self):
		self.board_queue.put(['servo{}'.format(self.entrance_id), 90])
		
	def close_door(self):
		self.board_queue.put(['servo{}'.format(self.entrance_id), 0])		
		
class PartyModeController(StatePredictor):
	
	def __init__(self, minifig_detector, music_preferences, board_queue, sweep_servo_id = 4, number_of_people_threshold = 4, update_interval = 2):
		self.minifig_detector = minifig_detector
		self.music_preferences = music_preferences
		self.sweep_servo_id = sweep_servo_id
		self.number_of_people_threshold = number_of_people_threshold
		states = {
			0 : State('do nothing', 0),
			1 : State('lets party', 1)
		}
		super(PartyModeController, self).__init__(states=states, sensors= [],board_queue=board_queue, update_interval = update_interval)
		scope = 'user-library-read'
		username="Giannhs Daras"
		try:
			token = util.prompt_for_user_token(username, scope)
		except:
			raise Exception('Error on spotify connection')

		assert(token)
		self.spotipy = spotipy.Spotify(auth=token)
		result=self.majority()
		t=self.spotipy.search(q=result,limit=1)
		for j,k in enumerate(t['tracks']['items']):
			pass
		self.track=k['preview_url']
		print(self.track)
		states[1].addSubscriber(self.party_rock())
			
	def update(self):
		
		if self.minifig_detector.number_of_people >= self.number_of_people_threshold:
			self.party_rock()
			
	def party_rock(self):		
		result_url = self.track			
		webbrowser.open_new(result_url)	
		
		for i in range(self.sweep_times):
			self.sweep(self.sweep_servo_id)
				
	def sweep(self, x):
		self.board_queue.put(['servo{}'.format(x), 180])
		time.sleep(1)
		self.board_queue.put(['servo{}'.format(x), 0])
		time.sleep(1)
	def majority(self):
		help_dict={}
		for it in self.music_preferences.values():
			help_dict[it]=0
		for it in self.music_preferences.values():
			help_dict[it]+=1
		t = max(zip(help_dict.keys(),help_dict.values()), key = lambda x : x[1])[0]
		return t


class HologramController(StatePredictor):
	def __init__(self,hologramQuery, board_queue, update_interval=1):
		states = {
		0:State('do nothing',0),
		1:State('update hologram',1)
		}
		sensors=[]
		self.firebase = firebase.FirebaseApplication('https://celeste-54d66.firebaseio.com/', None)
		self.peopleDict={0:'John',1:'Mary',2:'Marios',3:'Mike'}
		states[0].addSubscriber(self.updateHologram)
		super(HologramController, self).__init__(states = states, sensors = [], board_queue = board_queue, update_interval=update_interval)

		#train follows
		f1=open('./text_classification/john.txt','r')
		f2=open('./text_classification/mary.txt','r')
		f3=open('./text_classification/marios.txt','r')
		f4=open('./text_classification/mike.txt','r')
		temp=[]
		temp.append(''.join(f1.readlines()))
		temp.append(''.join(f2.readlines()))
		temp.append(''.join(f3.readlines()))
		temp.append(''.join(f4.readlines()))
		f1.close()
		f2.close()
		f3.close()
		f4.close()
		self.text_clf = Pipeline([('vect', CountVectorizer()),('tfidf', TfidfTransformer()),('clf', MultinomialNB()),])
		self.text_clf.fit(temp,[0,1,2,3])
		super(HologramController, self).__init__(states = states, sensors = [], update_interval=update_interval)

		
	def updateHologram(self, x):
		result=self.peopleDict[self.text_clf.predict(self.hologramQuery)[0]]
		self.firebase.put('/',{'url':result})



class EnergySaverController(StatePredictor):
	def __init__(self, update_interval, board):
		states = {
			0 : State('do nothing',0),
			1 : State('show message',1)
		}
		self.timeon=0
		self.counter=0
		states[1].addSubscriber(EnergySaverController.showmessage)
		sensors = [ledarray]
		super(EnergySaverController, self).__init__(states = states, sensors = sensors, update_interval=update_interval)

	def getData(self):
		x = np.array([])
		for sensor in self.sensors:
			d = sensor.getData()
			x = np.append(x, d)
		return x 
		
	def update(self):
		""" Update NN """

		print 'Updating'

		x = self.getData()
		self.timeon += sum(x)
		self.counter=self.counter+1
		self.timeon=normalize(self.timeon,l=0,r=24)
		if not self.queue.empty():
			index = self.queue.get()
		else:
			index = self.predict_next(self.timeon)

		# use softmax
		self.state = self.states[index]
		print ('New state: {0}'.format(self.states[index].name))

		# Retrain our model
		if self.counter == 15:
			self.counter =0
			print 'Retraining'
			y = keras.utils.to_categorical(index, self.num_classes)
			self.model.train_on_batch(np.array([self.timeon]), y)
			self.num_train += 1

		self.state.onActivation(None)
		
	def showmessage(self):
		print 'Daily usage exceeded'	
		self.board_queue.put(['ledarray'], [12, 13])
			

