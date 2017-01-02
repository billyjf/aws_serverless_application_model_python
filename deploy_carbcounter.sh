#!/bin/bash -xev
lambda_name=carbcounter

if [ ! -f lambda/$lambda_name/nutritionix.py ]
then
    pip install -t $lambda_name nutritionix
fi

aws cloudformation package --template cloudformation_lambda.yaml --s3-bucket billyjf.carbcounter | grep AWSTemplateFormatVersion -A -1 | tee cloudformation_lambda_deploy.yaml
aws cloudformation deploy --template cloudformation_lambda_deploy.yaml --stack-name lambda-carbcounter --capabilities CAPABILITY_IAM