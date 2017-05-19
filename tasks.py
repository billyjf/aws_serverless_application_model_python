from invoke import task
import os
import re
import requests

@task
def aws_creds_are_set(ctx, 
                      home):
  creds_file = "{0}/.aws/credentials".format(home)

  if not os.path.isfile(creds_file):
    print "Aws creds not set, setting them now."

    ctx.run("mkdir -p {0}/.aws".format(home))

    with open(creds_file, 'w') as creds:
      creds.write("""[default]
region=us-west-2
aws_access_key_id={0}
aws_secret_access_key={1}
""".format(os.environ['aws_access_key_id'], 
           os.environ['aws_secret_access_key']))

@task
def s3_site_publish(ctx):
  ctx.run("""aws s3 cp favicon.ico s3://cc.billyjf.com --acl public-read
aws s3 cp favicon.png s3://cc.billyjf.com --acl public-read
aws s3 cp index.html s3://cc.billyjf.com --acl public-read
aws s3 sync codebase/ s3://cc.billyjf.com/codebase/ --acl public-read""")

@task
def download_dependencies(ctx,
                          lambda_name):
  if not os.path.isfile("lambda/{0}/nutritionix.py".format(lambda_name)):
    ctx.run("pip install -t {0} nutritionix".format(lambda_name))

@task
def clean_python_lambda(ctx):
  ctx.run("rm -rf lambda/carbcounter/*.pyc")

@task
def zip_push_to_s3_and_generate_deployment_cloudformation(ctx):
  this_script_dir = os.path.dirname(os.path.abspath(__file__))

  with open("cloudformation/lambda.yaml", "r") as file:
    lambda_template = file.read()

  with open("cloudformation/lambda.yaml", "w") as out:
    out.write(re.sub(r"CodeUri:.*", 
                     "CodeUri: {0}/lambda".format(this_script_dir), 
                     lambda_template))

  ctx.run("aws cloudformation package --template cloudformation/lambda.yaml --s3-bucket billyjf.carbcounter | tail -n +2 | tee cloudformation/lambda_deploy.yaml")

@task
def cloudformation_deploy(ctx):
  ctx.run("aws cloudformation deploy --template cloudformation/lambda_deploy.yaml --stack-name lambda-carbcounter --capabilities CAPABILITY_IAM")

@task
def integration_test(ctx):
  get = "https://k2aks8qbq5.execute-api.us-west-2.amazonaws.com/prod/pizza"
  r = requests.get(get)

  if "Access-Control-Allow-Origin" not in r.headers:
    print "***** INTEGRATION TEST FAILURE: Access-Control-Allow-Origin Missing for {0}".format(get)
  else:
    print "***** INTEGRATION TEST SUCCESSFUL"