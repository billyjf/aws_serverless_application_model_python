'''
Follow these steps to complete the configuration of your command API endpoint

  1. When completing the blueprint configuration select "Open" for security
     on the "Configure triggers" page.

  2. Enter a name for your execution role in the "Role name" field.
     Your function's execution role needs kms:Decrypt permissions. We have
     pre-selected the "KMS decryption permissions" policy template that will
     automatically add these permissions.

  3. Update the URL for your Slack slash command with the invocation URL for the
     created API resource in the prod stage.
'''

#import boto3
import json
import logging
import os

from base64 import b64decode
from urlparse import parse_qs

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    #POST: params = parse_qs(event['body'])
    #token = params['token'][0]
    #if token != expected_token:
    #    logger.error("Request token (%s) does not match expected", token)
    #    return respond(Exception('Invalid request token'))

    #user = params['user_name'][0]
    #command = params['command'][0]
    #...
    search = event['pathParameters']['search']

    return respond(None, "SEARCH: {0}".format(search))

