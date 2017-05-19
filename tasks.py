from invoke import task
import os, sys
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
    ctx.run("pip install -U pip") # Ensure that --target is available
    ctx.run("pip install --target lambda/{0} nutritionix".format(lambda_name))

  ctx.run("ls -R lambda/{0}".format(lambda_name))

@task
def clean_python_lambda(ctx):
  ctx.run("rm -rf lambda/carbcounter/*.pyc")

@task
def zip_push_to_s3_and_generate_deployment_cloudformation(ctx):
  this_script_dir = os.path.dirname(os.path.abspath(__file__))

  with open("cloudformation/lambda.yaml", "r") as file:
    lambda_template = file.read()

  with open("cloudformation/lambda.yaml", "w") as out:
    lambda_template = re.sub(r"CodeUri:.*", 
                             "CodeUri: {0}/lambda".format(this_script_dir), 
                             lambda_template)
    lambda_template = re.sub(r"app_id:.*", 
                             'app_id: "{0}"'.format(os.environ['app_id']), 
                             lambda_template)
    lambda_template = re.sub(r"api_key:.*", 
                             'api_key: "{0}"'.format(os.environ['api_key']), 
                             lambda_template)

    out.write(lambda_template)

  ctx.run("aws cloudformation package --template cloudformation/lambda.yaml --s3-bucket billyjf.carbcounter | tail -n +2 | tee cloudformation/lambda_deploy.yaml")

@task
def cloudformation_deploy(ctx):
  ctx.run("aws cloudformation deploy --template cloudformation/lambda_deploy.yaml --stack-name lambda-carbcounter --capabilities CAPABILITY_IAM")

def test_failed(msg):
  print "***** INTEGRATION TEST FAILURE: {0}".format(msg)
  sys.exit(1)

@task
def integration_test(ctx):
  get = "https://k2aks8qbq5.execute-api.us-west-2.amazonaws.com/prod/pizza"
  r = requests.get(get)

  if r.status_code != 200:
    test_failed("Did not get HTTP 200, instead got {0}.".format(r.status_code))

  if "Access-Control-Allow-Origin" not in r.headers:
    test_failed("Access-Control-Allow-Origin Missing for {0}".format(get))
  else:
    print "***** INTEGRATION TEST SUCCESSFUL"