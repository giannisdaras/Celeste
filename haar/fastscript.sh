#!/bin/bash

find ./increased_negatives -iname "*.jpeg" > increased_negatives.txt &&
find ./positived -iname "*.jpeg" > increased_positives.txt &&


perl createsamples.pl increased_positives.txt increased_negatives.txt samples 5000 "opencv_createsamples -bgcolor 0 -bgthresh 0 -maxxangle 1.1 -maxyangle 1.1 maxzangle 0.5 -maxidev 40 -w 40 -h 40" &&
python mergevec.py -v samples -o samples.vec &&

opencv_traincascade -data leonidas -vec samples.vec -bg increased_negatives.txt -numStages 15 -minHitRate 0.999 -maxFalseAlarmRate 0.25 -numPos 2000 -numNeg 3000 -w 40 -h 40 -mode ALL -precalcValBBufSize 2048 -featureType LBP

