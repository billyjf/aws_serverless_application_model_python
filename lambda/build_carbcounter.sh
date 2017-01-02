#!/bin/bash -xev
lambda_name=carbcounter

if [ ! -f $lambda_name/nutritionix.py ]
then
    pip install -t $lambda_name nutritionix
fi

rm carbcounter.zip
zip -r carbcounter.zip carbcounter/* --exclude *.pyc
