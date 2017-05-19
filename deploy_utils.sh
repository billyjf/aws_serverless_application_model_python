#!/bin/bash -e
function download_dependencies() {
    if [ ! -f lambda/$1/nutritionix.py ]
    then
        pip install -t $1 nutritionix
    fi
}

function clean_python_lambda() {
    rm -rf lambda/carbcounter/*.pyc
}

function zip_push_to_s3_and_generate_deployment_cloudformation() {
    sed -i "s|CodeUri: .*|CodeUri: $(pwd)/cloudformation/lambda|g" cloudformation/lambda.yaml
    aws cloudformation package --template cloudformation/lambda.yaml --s3-bucket billyjf.carbcounter | tail -n +2 | tee cloudformation/lambda_deploy.yaml
}

function integration_test() {
    cmd='curl -v https://k2aks8qbq5.execute-api.us-west-2.amazonaws.com/prod/pizza 2>&1'
    result=$(eval $cmd | grep 'Access-Control-Allow-Origin' &>/dev/null; echo $?)
    if [ $result -eq 0 ]
    then
        echo "INTEGRATION TEST SUCCESSFUL"
    else
        echo "***** INTEGRATION TEST FAILURE: Access-Control-Allow-Origin Missing!"
        eval $cmd
        echo "***** INTEGRATION TEST FAILURE: Access-Control-Allow-Origin Missing!"
    fi
}

function aws_creds_are_set() {
    if [ ! -f $1 ]
    then
        echo "Aws creds not set, setting them now."
        mkdir -p ~/.aws

cat > $1 << EOF
[default]
region=us-west-2
aws_access_key_id=$aws_access_key_id
aws_secret_access_key=$aws_secret_access_key
EOF

    fi
}