from __init__ import *
from comm import *


class MinifigDetector(multiprocessing.Process):

    def __init__(self, camera=Camera(), update_interval=10, size=(100, 100)):
        super(MinifigDetector, self).__init__()
        self.model = Sequential()
        self.camera = camera
        self.size = size
        self.model.add(Convolution2D(16, kernel_size=(
            3, 3), padding='same', activation='relu', input_shape=(size[0], size[1], 1)))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.5))

        self.model.add(Convolution2D(32, kernel_size=(
            3, 3), padding='same', activation='relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.5))

        self.model.add(Flatten())
        self.model.add(Dense(1, activation='softmax'))
        self.model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])

        self.number_of_people = 0
        self.running = False
        self.update_interval = update_interval

    def train(self, img_dir, y, epochs=30, batch_size=128):
        current_dir = os.getcwd()
        os.chdir(img_dir)
        images = os.listdir('.')
        x = np.array([])
        for image in images:
            tmp = cv2.imread(image)
            self.transform(tmp)
            x = np.append(x, tmp)
        self.model.fit(x, y, epochs=epochs, batch_size=batch_size)
        os.chdir(current_dir)

    def transform(self, tmp):
        tmp = cv2.cvtColor(tmp, cv2.COLOR_BGR2GRAY)
        tmp = cv2.resize(tmp, self.size)
        tmp = tmp.reshape((self.size[0], self.size[0], 1))
        return tmp

    def update(self):
        x = self.transform(self.camera.getData(grayscale=False))
        self.number_of_people = int(round(self.model.predict(np.array([x]))))
        return self.number_of_people

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
