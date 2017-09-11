#!/bin/bash

find ./increased_negatives -iname "*.jpeg" > increased_negatives.txt &&
find ./increased_positives -iname "*.jpeg" > increased_positives.txt &&


perl createsamples.pl increased_positives.txt increased_negatives.txt samples 10000 "opencv_createsamples -bgcolor 0 -bgthresh 0 -maxxangle 1.1 -maxyangle 1.1 maxzangle 0.5 -maxidev 40 -w 40 -h 40" &&
python mergevec.py -v samples -o samples.vec &&

opencv_traincascade -data increased_lots -vec samples.vec -bg increased_negatives.txt -numStages 10 -minHitRate 0.999 -maxFalseAlarmRate 0.25 -numPos 5000 -numNeg 5000 -w 40 -h 40 -mode ALL -precalcValBBufSize 2048 -featureType LBP

