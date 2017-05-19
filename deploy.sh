#!/bin/bash -e
pip install invoke # task runner
pip install requests # http for humans

invoke aws_creds_are_set ~
invoke s3_site_publish
invoke download_dependencies carbcounter
invoke clean_python_lambda
invoke zip_push_to_s3_and_generate_deployment_cloudformation
invoke cloudformation_deploy
invoke integration_test

echo "******** DON'T FORGET MANUAL STEPS (on first deployment/iteration, not necessary for all future deployments):"
echo " 1. aws lambda add-permission --function-name [arn] --source-arn 'arn:aws:execute-api:us-west-2:649309545751:cruu7iixa4/*/*/carbcounter/*' --principal apigateway.amazonaws.com --statement-id efcea982-331a-4b0e-80d9-3edf5a5d3964 --action lambda:InvokeFunction"
echo " 2? Actions > Enable CORS > accept defaults given to you via cloudformation prior deploy (strange)."
echo " 4. Update client index.html and deploy static for new api gateway key --> factor this out in the future."
echo " 5. Final ui client test."