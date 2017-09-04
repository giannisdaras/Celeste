#!/usr/bin/env python

import cv2
import sys
import glob
import os
import time

debug = 1
obj_list = []
obj_count = 0
click_count = 0
x1 = 0
y1 = 0
h = 0
w = 0
key = None
frame = None

cmd = os.system
# mouse callback

def clean_dir():
    cmd('rm -rf positive* negative*')
    cmd('rm -rf classifier')

def train_haar_cascade():
    pass

def obj_marker(event,x,y,flags,param):
    global click_count
    global debug
    global obj_list
    global obj_count
    global x1
    global y1
    global w
    global h
    global frame
    if event == cv2.EVENT_LBUTTONDOWN:
        click_count += 1
        if click_count % 2 == 1:
            x1 = x
            y1 = y
        else:
            w = abs(x1 - x)
            h = abs(y1 - y)
            obj_count += 1
            if x1 > x:
                x1 = x
            if y1 > y:
                y1 = y
            obj_list.append((x1,y1,w,h))
            if debug > 0:
                print obj_list
            cv2.rectangle(frame,(x1 - 2 ,y1 - 2),(x1+w + 2,y1+h + 2),(255,255,255),2)
            cv2.imshow('frame',frame)

print 'Clean everything [y/n]?'
ans = raw_input().strip('\n')
if 'y' in ans:
    clean_dir()

print 'This is a dataset generator'
print 'We will start with the negative images first'
print 'Enter camera id: '
cam_id = int(raw_input().strip('\n'))
cam = cv2.VideoCapture(cam_id)

print 'Enter number of negative samples to be acquired: '
num_neg = int(raw_input().strip('\n'))
print 'Enter wait interval in seconds: '
update_interval = float(raw_input().strip('\n'))

neg_dir = './negative_images'
cwd = os.getcwd()
try:
    os.mkdir(neg_dir)
except:
    pass

print 'Acquiring Negatives'

neg_file = open('negatives.txt', 'w')
for i in range(num_neg):
    ret, img = cam.read()
    cv2.imwrite('{0}/{1}.jpg'.format(neg_dir, i + 1), img)
    print 'Sample {0} captured!'.format(i+1)
    neg_file.write('{0}/{1}.jpg\n'.format(neg_dir, i + 1))
    time.sleep(update_interval)
neg_file.close()

print 'Negatives : OK'


print 'Enter number of positive samples to be acquired for each person: '
num_pos = int(raw_input().strip('\n'))
print 'Enter wait interval in seconds: '
update_interval = float(raw_input().strip('\n'))
print 'Enter number of people: '
num_classes = int(raw_input())

pos_dir = './positive_images'

try:
    os.mkdir(pos_dir)
except:
    pass

print 'Enter resize dimensions (eg 40 40)'
size_x, size_y = map(int, raw_input().split(' '))

print 'Acrquiring positives'

for j in range(num_classes):
    print 'Enter person number {0} and press any key'.format(j)
    raw_input()
    for i in range(num_pos):
        ret, img = cam.read()
        cv2.imwrite('{0}/{1}.jpg'.format(pos_dir, i + 1), img)
        print 'Sample {0} captured!'.format(i+1)
        time.sleep(update_interval)

print "Now let's mark positives"

ordinals = [ord(str(i)) for i in range(num_classes)]

#getting list of jpgs files from
list = glob.glob('%s/*.jpg' % pos_dir)
if debug > 0:
    print list
#creating window for frame and setting mouse callback
cv2.namedWindow('frame',cv2.WINDOW_AUTOSIZE)
cv2.setMouseCallback('frame',obj_marker)
#creating a file handle
file_name = open('positives.txt',"w")
neural_data_file = open('{0}/neural_data.txt'.format(pos_dir), "w")
#loop to traverse through all the files in given path
for i in list:
    frame = cv2.imread(i)
    print i                                                  # reading file
    cv2.imshow('frame',frame)                                               # showing it in frame
    obj_count = 0                                                           #initializing obj_count
    key = cv2.waitKey(0)                                                    # waiting for user key
    #print key & 0xFF
    while((key & 0xFF != ord('q')) and (key & 0xFF != ord('n')) and (not(key & 0xFF % ord('0') <= num_classes - 1))):           # wait till key pressed is q or n
        key = cv2.waitKey(0)
        #print key & 0xFF

        if(key & 0xFF == ord('c')):                                         # if key press is c, cancel previous markings
            obj_count = 0                                                   # initializing obj_count and list
            obj_list = []
            frame = cv2.imread(i)                                           # read original file
            cv2.imshow("frame" ,frame)                                       # refresh the frame
    if(key & 0xFF == ord('q')):                                             # if q is pressed
        break                                                               # exit
    elif key & 0xFF % ord('0') <= num_classes - 1:
        if obj_count > 0:
            x, y, w, h = obj_list[0]
            print 'Cropping to window size {0}x{1}'.format(w,h)
            frame = frame[y : y + h , x : x + w ]
            frame = cv2.resize(frame, (size_x, size_y))
            cv2.imwrite('{0}'.format(i),frame)
            file_name.write('{0}\n'.format(i))
            neural_data_file.write('{0} {1}\n'.format(i, (key & 0xFF) % ord('0')))
            obj_count = 0
            obj_list = []
    elif(key & 0xFF == ord('n')):                                           # if n is pressed
        obj_count = 0
        obj_list = []

file_name.close()
neural_data_file.close()
cv2.destroyAllWindows()
cam.release()

# TODO Haar training

print 'Start Haar-Classifier training? [y/n]:'
ans = raw_input().strip('\n')
if not ()'y' in ans):
    sys.exit(0)
