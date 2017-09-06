import cv2
id_ = 1
csc = cv2.CascadeClassifier('./classifier/cascade.xml')
global cam

cam = cv2.VideoCapture(id_)

def detect(i):
	global cam
	ret, img = cam.read()
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	res = csc.detectMultiScale(gray, 45, 45)
	print 'Found {0}'.format(len(res))
	for x,y,w,h in res:
		cv2.rectangle(gray,(x,y),(x+w,y+h),(255,0,0),2)
	
	cv2.imwrite('result{}.jpg'.format(i), gray)

for i in range(10):
	detect(i)
