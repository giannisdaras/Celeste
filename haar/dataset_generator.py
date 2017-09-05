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

def clean_dir():
    cmd('rm -rf positive* negative*')
    cmd('rm -rf classifier')
    cmd('rm -rf samples*')


def obj_marker(event, x, y, flags, param):
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
            obj_list.append((x1, y1, w, h))
            if debug > 0:
                print obj_list
            cv2.rectangle(frame, (x1 - 2, y1 - 2),
                          (x1 + w + 2, y1 + h + 2), (255, 255, 255), 2)
            cv2.imshow('frame', frame)


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

#neg_file = open('negatives.txt', 'w')
for i in range(num_neg):
    ret, img = cam.read()
    cv2.imwrite('{0}/{1}.jpg'.format(neg_dir, i + 1), img)
    print 'Sample {0} captured!'.format(i + 1)
    #neg_file.write('{0}/{1}.jpg\n'.format(neg_dir, i + 1))
    time.sleep(update_interval)
#neg_file.close()

cmd('find ./negative_images -iname "*.jpg" > negatives.txt')

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

x = 1
for j in range(num_classes):
    print 'Enter person number {0} and press any key'.format(j)
    raw_input()
    for i in range(num_pos):
        ret, img = cam.read()
        cv2.imwrite('{0}/{1}.jpg'.format(pos_dir, x), img)
        print 'Sample {0} captured!'.format(i + 1)
        time.sleep(update_interval)
        x += 1

try:
    cam.release()
    del cam
except:
    pass
finally:
    cam = cv2.VideoCapture(cam_id)

print "Now let's mark positives"

ordinals = [ord(str(i)) for i in range(num_classes)]

# getting list of jpgs files from
list = glob.glob('%s/*.jpg' % pos_dir)
if debug > 0:
    print list
# creating window for frame and setting mouse callback
cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE)
cv2.setMouseCallback('frame', obj_marker)
# creating a file handle
neural_data_file = open('{0}/neural_data.txt'.format(pos_dir), "w")
# loop to traverse through all the files in given path
for i in list:
    frame = cv2.imread(i)
    print i                                                  # reading file
    # showing it in frame
    cv2.imshow('frame', frame)
    obj_count = 0  # initializing obj_count
    # waiting for user key
    key = cv2.waitKey(0)
    # print key & 0xFF
    # wait till key pressed is q or n
    while((key & 0xFF != ord('q')) and (key & 0xFF != ord('n')) and (not(key & 0xFF % ord('0') <= num_classes - 1)) and (key & 0xFF != ord('d'))):
        key = cv2.waitKey(0)
        # print key & 0xFF

        # if key press is c, cancel previous markings
        if(key & 0xFF == ord('c')):
            # initializing obj_count and list
            obj_count = 0
            obj_list = []
            # read original file
            frame = cv2.imread(i)
            # refresh the frame
            cv2.imshow("frame", frame)
    if(key & 0xFF == ord('q')):                                             # if q is pressed
        break                                                               # exit
    elif key & 0xFF % ord('0') <= num_classes - 1:
        if obj_count > 0:
            x, y, w, h = obj_list[0]
            print 'Cropping to window size {0}x{1}'.format(w, h)
            frame = frame[y: y + h, x: x + w]
            frame = cv2.resize(frame, (size_x, size_y))
            cv2.imwrite('{0}'.format(i), frame)
            neural_data_file.write(
                '{0} {1}\n'.format(i, (key & 0xFF) % ord('0')))
            obj_count = 0
            obj_list = []
    elif(key & 0xFF == ord('n')):                                           # if n is pressed
        obj_count = 0
        obj_list = []
    elif key & 0xFF == ord('d'):
        obj_list = []
        obj_count = 0
        os.remove(i)

neural_data_file.close()
cv2.destroyAllWindows()
cam.release()

cmd('find ./positive_images -iname "*.jpg" > positives.txt')

# TODO Haar training

print 'Start Haar-Classifier training? [y/n]:'
ans = raw_input().strip('\n')
if not ('y' in ans):
    sys.exit(0)

print 'User perl script to generate samples? [y/n]'
ans = raw_input().strip('\n')

cr_smp = 'opencv_createsamples -bgcolor 0 -bgthresh 0 -maxxangle 1.1 -maxyangle 1.1 -maxzangle 0.5 -maxidev 40 -w {} -h {}'.format(
    size_x, size_y)

if 'y' in ans:
    print 'Generating Samples: How many samples do you want? [default 7000]'
    num_samples = int(raw_input())

    cmd('perl createsamples.pl  positives.txt negatives.txt samples {} "{}"'.format(
        num_samples, cr_smp))
else:
    cmd(cr_smp)

print 'Merging samples with mergevec'

import mergevec

mergevec.merge_vec_files('samples/', 'samples.vec')

print 'Enter number of stages'
numStages = int(raw_input())

try:
    os.mkdir('classifier')
except:
    pass

print 'Starting training'
cmd('''opencv_traincascade -data classifier -vec samples.vec -bg negatives.txt\
   -numStages {} -minHitRate 0.999 -maxFalseAlarmRate 0.5 -numPos 1000\
   -numNeg 600 -w {} -h {} -mode ALL -precalcValBufSize 1024\
   -precalcIdxBufSize 1024 -featureType LBP'''.format(numStages, size_x, size_y))

print 'training completed!'
sys.exit(0)
