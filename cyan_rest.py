from django.http import HttpRequest, HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
import logging
import os
from django.http import JsonResponse
import requests

def get_location_data(request):
    """
    get cyan data by lat long location
    """
    print('Inside get_location_data')
    baseURL = os.getenv('CYAN_REST_SERVER')
    data = request.body
    # url = baseURL + '/location/data/28.6138/-81.6227/2017-12-08'
    # url = 'https://cyan.epa.gov/cyan/cyano/location/data/28.6138/-81.6227/2017-12-08'
    resp = requests.get('https://cyan.epa.gov/cyan/cyano/location/data/28.6138/-81.6227/2017-12-08')
    print(resp.status_code)
    print type(resp)
    # return web_call_new(url)
    return resp


# def web_call_new(url, data=None):
# 	"""
# 	Makes the request to a specified URL
# 	and POST data. Returns resonse data as dict
# 	"""
#
# 	# TODO: Deal with errors more granularly... 403, 500, etc.
# 	try:
# 		if data == None:
# 			response = requests.get(url, timeout=10)
# 		else:
# 			response = requests.post(url, data=json.dumps(data), headers=headers, timeout=10)
# 		return json.loads(response.content)
# 	except requests.exceptions.RequestException as e:
# 		logging.warning("error at web call: {} /error".format(e))
# 		raise e
# print('Inside web')