from __init__ import *
from comm import Camera
from keras.preprocessing.image import ImageDataGenerator

global THRESHOLD
THRESHOLD = 0.75
global sgd

sgd = keras.optimizers.SGD(lr=0.1, decay=1e-2, momentum=0.9)


# Holds minifig information

class Minifig:
	def __init__(self, name):
		self.name = name
		self.preferences = {}  # holds preferences like music etc

	def __getitem__(self, item):
		return self.preferences[item]

	def __setitem__(self, item, value):
		try:
			self.preferences[item].append(value)
		except KeyError:
			self.preferences[item] = [value]


class MinifigDetector(multiprocessing.Process):
	
	def add_stage(self, i, f = lambda x : 2**(4 + x)):
		print 'Added conv with {0} filters'.format(f(i))
		self.model.add(Convolution2D(f(i), kernel_size=(
			3, 3), padding='same', activation='relu'))
		self.model.add(MaxPooling2D(pool_size=(2, 2)))
		#self.model.add(Dropout(0.2))
	
	def __init__(self, minifigs, status,camera, num_stages=3, grayscale=True, update_interval=10, size=(40, 40), cascade_classifier='classifier.xml', suppress_classification = False):
		super(MinifigDetector, self).__init__()
		self.model = Sequential()
		self.camera = Camera(index = camera)
		self.size = size
		self.lego_face_classifier = cv2.CascadeClassifier(cascade_classifier)
		self.grayscale = grayscale
		self.num_classes = len(minifigs)
		self.minifigs = minifigs
		
		self._class_labels = multiprocessing.Array(c_char_p, map(lambda x : x.name, self.minifigs))
		
		
		self.model.add(Convolution2D(32, kernel_size=(
			3, 3), padding='same', activation='relu', input_shape=(size[0], size[1], 1 if grayscale else 3)))
		
		self.model.add(MaxPooling2D(pool_size=(2, 2)))
		self.model.add(Dropout(0.5))
		
		for i in range(1, num_stages):
			self.add_stage(i)	
		
		self.model.add(Dropout(0.25))
		self.model.add(Flatten())
		self.model.add(Dense(128, activation='relu'))
		self.model.add(Dropout(0.5))
		self.model.add(Dense(self.num_classes, activation='softmax'))

		
		self.model.compile(loss=keras.losses.categorical_crossentropy,
			  optimizer=keras.optimizers.Adadelta(),
			  metrics=['accuracy'])
		
		self.datagen = ImageDataGenerator(
			rotation_range=40,
			width_shift_range=0.2,
			height_shift_range=0.2,
			rescale=1./255,
			shear_range=0.2,
			zoom_range=0.2,
			horizontal_flip=True,
			fill_mode='nearest')
			
			
		self.train_generator = self.datagen.flow_from_directory(
		'./positive_images',  # this is the target directory
		target_size=self.size,  # all images will be resized to 150x150
		batch_size=128,
		class_mode='categorical',
		classes=[str(i) for i in range(self.num_classes)]
		)
		
		self.suppress_classification = suppress_classification
		self._number_of_people = multiprocessing.Value('i', 0)
		self._running = multiprocessing.Value('b', True)
		self.update_interval = update_interval
		self.status = status
		
		
		for lbl in self._class_labels:
			self.status[lbl] = 0
			
	@property
	def number_of_people(self):
		return self._number_of_people.value
	
	@number_of_people.getter
	def number_of_people(self):
		return self._number_of_people.value
		
	@number_of_people.setter
	def number_of_people(self, x):
		self._number_of_people.value = x
		
	def reset_status(self):
		self.number_of_people = 0
		for lbl in self._class_labels:
			self.status[lbl] = 0

	def get_data(self, source_file, onehot=False, delimiter=' '):	
		images = []
		y = np.array([])
		with open(source_file, 'r') as f:
			while True:
				l = f.readline()
				if f is None:
					break
				l = l.strip('\n').split(delimiter)
				if len(l) == 2:
					images.append(l[0])
					y = np.append(y, l[1])
				else:
					break
		y = y.reshape((len(y), 1))
		x = np.array([])
		
		if not onehot:
			y = keras.utils.to_categorical(y, self.num_classes)
		#print y
		print images
		for image in images:
			print image
			tmp = cv2.imread(image)
			tmp = self.transform(tmp)
			
			x = np.append(x, tmp)	
		x = x.reshape((len(y), self.size[1], self.size[0], 1 if self.grayscale else 3))
		return x, y

	def train_cnn(self, source_file, onehot=False, delimiter=' ', epochs=100, batch_size=128, generate_samples=False, generate_sample_per_image = 10):
		x, y = self.get_data(source_file=source_file, onehot=onehot, delimiter=delimiter)
		x_prime, y_prime = np.array([]), np.array([])
		
		if generate_samples:		
			for i in range(len(x)):
				i = 0
				while i < generate_sample_per_image:
					xi_prime = self.datagen.flow(x, batch_size=1, save_to_dir='{0}'.format(
						np.where(y[i]==1)[0][0]),
						save_prefix='gen',
						save_format='jpeg')	
					x_prime = np.append(x_prime, xi_prime)
					y_prime = np.append(y[i], y_prime)
					i += 1
			x_prime = x_prime.reshape((len(y_prime), self.size[1], self.size[0], 1 if self.grayscale else 3))
			y_prime = y_prime = y_prime.reshape((len(y_prime), 1))
			
			x = np.concatenate(x, x_prime)
			y = np.concatenate(y, y_prime)
				
		self.model.fit(x, y, epochs=epochs, batch_size=batch_size)
				
		
	def transform(self, tmp):
		if self.grayscale:
			tmp = cv2.cvtColor(tmp, cv2.COLOR_BGR2GRAY)
		if tmp.shape[0] != self.size[1] or tmp.shape[1] != self.size[0]:
			tmp = cv2.resize(tmp, self.size)
		tmp = tmp.reshape((self.size[0], self.size[1], 1 if self.grayscale else 3))
		tmp //= 255
		return tmp

	def predict_face(self, x, verbose):
		y = self.model.predict(np.array([x])).flatten()
		if verbose:
			for i in range(self.num_classes):
				print 'Person: {0}, Probability: {1}'.format(self._class_labels[i], y[i])
				
		# Apply threshold in case probabilities are low
		y = np.array(map(lambda x: x if x >= THRESHOLD else 0.0, y))
		index = np.argmax(y)
		if y[index] != 0.0:
			self.number_of_people += 1
			self.status[self._class_labels[index]] = 1
		else:
			pass
			# TODO add new habitats (how? if NN has fixed output?)

		return index, self._class_labels[index]

	def update(self, verbose=False):
		self.reset_status()
		img = self.camera.getData(grayscale=False)
		lego_faces = self.lego_face_classifier.detectMultiScale(img,
		scaleFactor=1.1,
		minNeighbors=5,
		minSize=(20,20),
		maxSize=(60,60))
		if verbose:
			print 'Found {0} potential matches'.format(len(lego_faces))
		self.number_of_people = len(lego_faces)

		 # Draw a rectangle around the faces
		for (x, y, w, h) in lego_faces:
			cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

		# Display the resulting frame
		cv2.imshow('Video', img)
		for (x, y, w, h) in lego_faces:
			cropped = self.transform(img[y: y + h, x: x + w])
			print cropped.shape
			if not self.suppress_classification:
				print 
				self.predict_face(cropped, verbose=verbose)

		if verbose:
			print self.status
		return self.status

	def resume(self):
		self.running = True

	def pause(self):
		self.running = False

	def run(self):
		self.resume()
		while True:
			while self.running:
				self.update()
				time.sleep(self.update_interval)
				
	def evaluate(self, source_file='neural_data_test.txt', delimiter=' ', onehot=False):
		current_dir = os.getcwd()
		images = []
		y = np.array([])
		with open(source_file, 'r') as f:
			while True:
				l = f.readline()
				if f is None:
					break
				l = l.strip('\n').split(delimiter)
				if len(l) == 2:
					images.append(l[0])
					y = np.append(y, l[1])
				else:
					break
		y = y.reshape((len(y), 1))
		x = np.array([])
		
		if not onehot:
			y = keras.utils.to_categorical(y, self.num_classes)
		#print y

		for image in images:
			tmp = cv2.imread(image)
			tmp = self.transform(tmp)
			x = np.append(x, tmp)
		x = x.reshape((len(y), self.size[1], self.size[0], 1 if self.grayscale else 3))
		self.score = self.model.evaluate(x, y, verbose=1)
		print('\nTest loss:', self.score[0])
		print('Test accuracy:', self.score[1])
		
	@property
	def class_labels(self):
		return list(self._class_labels)
		
	@class_labels.getter
	def class_labels(self, i):
		return self._class_labels[i]

	@class_labels.setter
	def class_labels(self, i, lbl):
		self._class_labels[i] = lbl
		
	@property
	def running(self):
		return self._running.value == True
		
	@running.setter
	def running(self, b):
		self._running.value = b
		
	@running.getter
	def running(self):
		return self._running.value == True
		
		


def initialize_from_directory(names,status, camera_id, update_interval=10, source_dir='../haar', neural_data_filename = 'neural_data.txt', new_weights=False):
	cwd = os.getcwd()
	os.chdir(source_dir)
	cascade = 'classifier/cascade.xml'
	minifigs = [Minifig(x) for x in names]
	minifig_detector = MinifigDetector(status=status,camera=camera_id, grayscale=True,
		minifigs=minifigs, update_interval=update_interval,  cascade_classifier=cascade)
	try:
		if not new_weights:	
			minifig_detector.model.load_weights('weights.h5')
	except:
		pass
	finally:
		if new_weights:
			minifig_detector.train_cnn(neural_data_filename)
			minifig_detector.model.save_weights('weights.h5')
	
	os.chdir(cwd)
	return minifig_detector


if __name__ == '__main__':
	minifig_detector = initialize_from_directory(names  =['John', 'Mario', 'Mary', 'Mike','Roberto'], camera_id = 1, update_interval = 5, status = {}, neural_data_filename='neural_data.txt', new_weights=False)
	minifig_detector.start()
	os.chdir('../haar/')
	
