#!/bin/bash -e
source deploy_utils.sh

aws_creds_are_set ~/.aws/credentials

aws s3 cp favicon.ico s3://cc.billyjf.com --acl public-read
aws s3 cp favicon.png s3://cc.billyjf.com --acl public-read
aws s3 cp index.html s3://cc.billyjf.com --acl public-read
aws s3 sync codebase/ s3://cc.billyjf.com/codebase/ --acl public-read

download_dependencies carbcounter
clean_python_lambda

zip_push_to_s3_and_generate_deployment_cloudformation
aws cloudformation deploy --template cloudformation/lambda_deploy.yaml --stack-name lambda-carbcounter --capabilities CAPABILITY_IAM
integration_test

echo "******** DON'T FORGET MANUAL STEPS (on first deployment/iteration, not necessary for all future deployments):"
echo " 1. aws lambda add-permission --function-name [arn] --source-arn 'arn:aws:execute-api:us-west-2:649309545751:cruu7iixa4/*/*/carbcounter/*' --principal apigateway.amazonaws.com --statement-id efcea982-331a-4b0e-80d9-3edf5a5d3964 --action lambda:InvokeFunction"
echo " 2? Actions > Enable CORS > accept defaults given to you via cloudformation prior deploy (strange)."
echo " 4. Update client index.html and deploy static for new api gateway key --> factor this out in the future."
echo " 5. Final ui client test."