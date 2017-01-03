#!/bin/bash -xev
lambda_name=carbcounter

aws s3 cp favicon.ico s3://billyjf.carbcounter.public --acl public-read
aws s3 cp favicon.png s3://billyjf.carbcounter.public --acl public-read
aws s3 cp index.html s3://billyjf.carbcounter.public --acl public-read
aws s3 sync codebase/ s3://billyjf.carbcounter.public/codebase/ --acl public-read

if [ $1 == "static" ]
then
    exit 0
fi

if [ ! -f lambda/$lambda_name/nutritionix.py ]
then
    pip install -t $lambda_name nutritionix
fi

if [ -f carbcounter.zip ]
then
    rm carbcounter.zip
fi

# Until `aws cloudformation deploy` supports deploying changes made to the python code, this is still
# a necessary option.
cd lambda
zip -r ../carbcounter.zip carbcounter/* --exclude *.pyc
cd ..

if [ "$1" != "zip" ]
then
    aws cloudformation package --template cloudformation_lambda.yaml --s3-bucket billyjf.carbcounter | grep AWSTemplateFormatVersion -A -1 | tee cloudformation_lambda_deploy.yaml
    aws cloudformation deploy --template cloudformation_lambda_deploy.yaml --stack-name lambda-carbcounter --capabilities CAPABILITY_IAM
    echo "******** DON'T FORGET MANUAL STEPS:"
    echo " 1. aws lambda add-permission --function-name [arn] --source-arn 'arn:aws:execute-api:us-west-2:649309545751:cruu7iixa4/*/*/carbcounter/*' --principal apigateway.amazonaws.com --statement-id efcea982-331a-4b0e-80d9-3edf5a5d3964 --action lambda:InvokeFunction"
    echo " 2? Actions > Enable CORS > accept defaults given to you via cloudformation prior deploy (strange)."
    echo " 3. Lambda > Save via zip (cloudformation deploy not deploying latest?)"
    echo " 4. Update client index.html and deploy static for new api gateway key --> factor this out in the future."
    echo " 5. Final ui client test."
fi