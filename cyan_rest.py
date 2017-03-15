from django.http import HttpRequest, HttpResponse
import os
import json
import requests


def get_location_data(request):
    """
    get cyan data by lat long location
    """
    print('Inside get_location_data')
    baseURL = os.getenv('CYAN_REST_SERVER')
    print(baseURL)
    data = (request.POST)
    print(data)
    latitude = data['latitude']
    print(latitude)
    longitude = data['longitude']
    print(longitude)
    date = data['date']
    print(date)
    url = "{0}/location/data/{1}/{2}/{3}".format(baseURL, latitude, longitude, date)
    print(url)
    resp = requests.get(url)
    resp2 = HttpResponse(resp.content, content_type='application/json')
    print(resp2)
    print(resp.content)
    return resp2