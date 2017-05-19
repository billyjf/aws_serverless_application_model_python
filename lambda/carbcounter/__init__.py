from nutritionix import Nutritionix
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
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Expose-Headers': 'Webix-Token',
        },
    }

def lambda_handler(event, context):
    search = ""

    if event != None and 'pathParameters' in event:
        search = event['pathParameters']['search']

    if len(search) > 0:
        nix = Nutritionix(app_id=os.environ["app_id"],
                          api_key=os.environ["api_key"])

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
    
    return respond(None, results['hits'])

