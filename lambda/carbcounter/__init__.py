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
from nutritionix import Nutritionix
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
    search = ""

    if event != None and 'pathParameters' in event:
        search = event['pathParameters']['search']

    if len(search) > 0:
        nix = Nutritionix(app_id="***REMOVED***",
                          api_key="***REMOVED***")

        #nix_results = nix.search(search).json()
        nix_results = nix.search().nxql(
            fields=["item_id",
                    "item_name",
                    "brand_name",
                    "nf_total_carbohydrate"],
            query=search).json()
    else:
        nix_results = {'hits': []}

    results = {'hits': []}

    count = 0
    for hit in nix_results['hits']:
        if hit['fields']['nf_total_carbohydrate'] is not None:
            results['hits'].append({'id': count,
                                    'value': '%s, %s, %sg' % ( hit['fields']
                                                                  ['item_name'],
                                                               hit['fields']
                                                                  ['brand_name'],
                                                               hit['fields']
                                                                  ['nf_total_carbohydrate'] )})
        count += 1
        pass

    return respond(None, results)

