from __init__ import *
from comm import Camera

global THRESHOLD
THRESHOLD = 0.75

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

    @staticmethod
    def majority_vote(minifigs, preference):
        pass


class MinifigDetector(multiprocessing.Process):

    def __init__(self, minifigs, camera=Camera(), update_interval=10, size=(40, 40), cascade_classifier='classifier.xml'):
        super(MinifigDetector, self).__init__()
        self.model = Sequential()
        self.camera = camera
        self.size = size
        self.lego_face_classifier = cv2.CascadeClassifier(cascade_classifier)

        self.num_classes = len(minifigs)
        self.minifigs = minifigs
        self.class_labels = map(lambda x: x.name, self.minifigs)
        self.model.add(Convolution2D(16, kernel_size=(
            3, 3), padding='same', activation='relu', input_shape=(size[0], size[1], 3)))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.5))

        self.model.add(Convolution2D(32, kernel_size=(
            3, 3), padding='same', activation='relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.5))

        self.model.add(Flatten())
        self.model.add(Dense(self.num_classes, activation='softmax'))
        self.model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])

        self.number_of_people = 0
        self.running = False
        self.update_interval = update_interval
        self.status = {}
        for lbl in self.class_labels:
            self.status[lbl] = 0

    def reset_status(self):
        self.number_of_people = 0
        for lbl in self.class_labels:
            self.status[lbl] = 0

    def train_cnn(self, source_file, onehot=False, delimiter=' ', epochs=30, batch_size=128):
        data = np.genfromtxt(source_file, delimiter=delimiter)
        images = data[:, 0]
        y = data[:, 1]

        if not onehot:
            y = keras.utils.to_categorical(y, self.num_classes)

        for image in images:
            tmp = cv2.imread(image)
            self.transform(tmp)
            x = np.append(x, tmp)
        self.model.fit(x, y, epochs=epochs, batch_size=batch_size)
        os.chdir(current_dir)

    def transform(self, tmp, grayscale=False):
        if grayscale:
            tmp = cv2.cvtColor(tmp, cv2.COLOR_BGR2GRAY)
        tmp = cv2.resize(tmp, self.size)
        tmp = tmp.reshape((self.size[0], self.size[0], 1 if grayscale else 3))
        return tmp

    def predict_face(self, x, verbose):
        y = self.model.predict(np.array([x])).flatten()
        if verbose:
            for i in range(self.num_classes):
                print 'Person: {0}, Probability: {1}'.format(self.class_labels[i], y[i])

        # Apply threshold in case probabilities are low
        y = np.array(map(lambda x: x if x >= THRESHOLD else 0.0, y))
        index = np.argmax(y)
        if y[index] != 0.0:
            self.number_of_people += 1
            self.status[self.class_labels[index]] = 1
        else:
            pass
            # TODO add new habitats (how? if NN has fixed output?)

        return index, self.class_labels[index]

    def update(self, verbose=True):
        self.reset_status()
        img = self.camera.getData(grayscale=False)
        lego_faces = self.lego_face_classifier.detectMultiScale(img)
        if verbose:
            print 'Found {0} potential matches'.format(len(lego_faces))

        for (x, y, w, h) in lego_faces:
            cropped = self.transform(img[y: y + h, x: x + w])
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


def initialize_from_directory(names, update_interval, source_dir='../haar'):
    cwd = os.getcwd()
    os.chdir(source_dir)
    cascade = 'classifier/cascade.xml'
    minfigs = [Minifig(x) for x in names]
    minifig_detector = MinifigDetector(
        minifigs, update_interval=update_interval, cascade_classifier=cascade)
    minifig_detector.train_cnn('positive_images/neural_data.txt')
    minifig.model.save_weights('weights.h5')
    os.chdir(cwd)
    return minifig_detector
