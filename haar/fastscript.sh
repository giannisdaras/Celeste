#!/bin/bash

find ./negative_images -iname "*.jpg" > negatives.txt &&
find ./positive_images -iname "*.jpg" > positives.txt &&


perl createsamples.pl positives.txt negatives.txt samples 2000 "opencv_createsamples -bgcolor 0 -bgthresh 0 -maxxangle 1.1 -maxyangle 1.1 maxzangle 0.5 -maxidev 40 -w 40 -h 40" &&
python mergevec.py -v samples -o samples.vec

nohup opencv_traincascade -data classifier -vec samples.vec -bg negatives.txt -numStages 10 -minHitRate 0.999 -maxFalseAlarmRate 0.5 -numPos 900 -numNeg 1800 -w 40 -h 40 -mode ALL -precalcValBBufSize 2048 -featureType LBP &

