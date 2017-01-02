from bottle import route, default_app, response
from json import dumps
from nutritionix import Nutritionix

@route('/search/<by_name>')
def search(by_name):
    if len(by_name) > 0:
        nix = Nutritionix(app_id="***REMOVED***",
                          api_key="***REMOVED***")

        #nix_results = nix.search(by_name).json()
        nix_results = nix.search().nxql(
            fields=["item_id",
                    "item_name",
                    "brand_name",
                    "nf_total_carbohydrate"],
            query=by_name).json()
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

    response.content_type = 'application/json'
    return dumps(results['hits'])

application = default_app()