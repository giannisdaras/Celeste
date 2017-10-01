import cv2

cams = [cv2.VideoCapture(i) for i in [0,1,2,3] ]

for i, cam in enumerate(cams):
	ret, frame = cam.read()
	cv2.imwrite('{}.jpg'.format(i), frame)
	cam.release()

