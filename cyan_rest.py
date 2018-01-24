from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os
import json
import requests


@csrf_exempt
def get_location_data(request):
    """
    get cyan data by lat long location
    """
    baseURL = 'https://cyan.epa.gov/cyan/cyano'
    # baseURL = os.getenv('CYAN_REST_SERVER')
    data = (request.POST)
    latitude = data['latitude']
    longitude = data['longitude']
    date = data['date']
    url = "{0}/location/data/{1}/{2}/{3}".format(baseURL, latitude, longitude, date)
    print('Cyan REST data request. Latitude: ' + str(latitude) + ', Longitude: ' + str(longitude) + ', Date: ' + str(date))
    resp = requests.get(url)
    resp2 = HttpResponse(resp.content, content_type='application/json')
    return resp2