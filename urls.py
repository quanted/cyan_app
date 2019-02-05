"""
Definition of urls for qed_cyan.
"""

from datetime import datetime
from django.conf.urls import url
from django.urls import path
import django.contrib.auth.views
from . import views, description, map, freqMap, lakecomparison, dot_map
from . import dashboard, algorithms, references, cyan_rest, cyandata_restapi, web_app_api


# if settings.IS_PUBLIC:
urlpatterns = [
    # # front end urls, django 1.0
    # url(r'^$', description.description_page, {'model': 'cyan'}),
    # url(r'^map/', map.map_page, {'model': 'cyan'}),
    # url(r'^freqMap$', freqMap.freqMap_page, {'model': 'cyan'}),
    # url(r'^lakecomparison$', lakecomparison.lakecomparison_page, {'model': 'cyan'}),
    # url(r'^dot_map', dot_map.dotmap_page, {'model': 'cyan'}),
    # url(r'^dashboard$', dashboard.dashboard_page, {'model': 'cyan'}),
    # url(r'^algorithms$', algorithms.algorithm_page, {'model': 'cyan'}),
    # url(r'^references$', references.references_page, {'model': 'cyan'}),
    #
    # url(r'^rest/api/v1/(?P<state>\w+)$', cyandata_restapi.getcyan_state_data, {'model': 'cyan'}),
    # url(r'^rest/api/v1/(?P<state>\w+)/(?P<year>\d{4})$', cyandata_restapi.getcyan_state_data_yearly, {'model': 'cyan'}),
    # url(r'^rest/api/v1/(?P<state>\w+)/lakes$', cyandata_restapi.getcyan_state_lake_data, {'model': 'cyan'}),
    # url(r'^rest/api/v1/(?P<state>\w+)/lakes/(?P<year>\d{4})$', cyandata_restapi.getcyan_state_lake_data_yearly, {'model': 'cyan'}),
    # url(r'^rest/api/v1/(?P<state>\w+)/lakes/info$', cyandata_restapi.getcyan_state_lake_info, {'model': 'cyan'}),
    # url(r'^rest/api/v1/(?P<state>\w+)/lakes/info/(?P<year>\d{4})$', cyandata_restapi.getcyan_state_lake_info_yearly,
    #     {'model': 'cyan'}),
    # url(r'^rest/api/v1/lake/(?P<lake>\w+)$', cyandata_restapi.getcyan_lake_data, {'model': 'cyan'}),
    # url(r'^rest/api/v1/lake/(?P<lake>\w+)/(?P<year>\d{4})$', cyandata_restapi.getcyan_lake_data_yearly, {'model': 'cyan'}),
    # url(r'^rest/api/v1/lake/(?P<lake>\w+)/info$', cyandata_restapi.getcyan_lake_info, {'model': 'cyan'}),
    # url(r'^rest/api/v1/lake/(?P<lake>\w+)/info/(?P<year>\d{4})$', cyandata_restapi.getcyan_lake_info_yearly, {'model': 'cyan'}),
    # # url(r'^rest/api/v1/lakes$', cyandata_restapi.getcyan_all_lake_data, {'model': 'cyan'}),
    # url(r'^rest/api/v1/lakes/info$', cyandata_restapi.getcyan_all_lake_info, {'model': 'cyan'}),
    # url(r'^rest/api/v1/lakes/info/(?P<year>\d{4})$', cyandata_restapi.getcyan_all_lake_info_yearly,
    #     {'model': 'cyan'}),
    #
    # # url(r'^api$', rest.rest_page, {'model': 'cyan'}),
    # # url(r'^swag$', views.getSwaggerJsonContent)
    #
    # # rest urls
    # url(r'^rest/location/data$', cyan_rest.get_location_data),
    # # url(r'^.*/$', description.description_page, {'model': 'cyan'})

    # front end urls, django 2.0
    path('', description.description_page, {'model': 'cyan'}),
    path('map/', map.map_page, {'model': 'cyan'}),
    path('freqMap/', freqMap.freqMap_page, {'model': 'cyan'}),
    path('lakecomparison/', lakecomparison.lakecomparison_page, {'model': 'cyan'}),
    path('dot_map/', dot_map.dotmap_page, {'model': 'cyan'}),
    path('dashboard/', dashboard.dashboard_page, {'model': 'cyan'}),
    path('algorithms/', algorithms.algorithm_page, {'model': 'cyan'}),
    path('references/', references.references_page, {'model': 'cyan'}),
    path('rest/api/v1/<str:state>/', cyandata_restapi.getcyan_state_data, {'model': 'cyan'}),
    path('rest/api/v1/<str:state>/<int:year>/', cyandata_restapi.getcyan_state_data_yearly, {'model': 'cyan'}),
    path('rest/api/v1/(<str:state>/lakes/', cyandata_restapi.getcyan_state_lake_data, {'model': 'cyan'}),
    path('rest/api/v1/<str:state>/lakes/<int:year>/', cyandata_restapi.getcyan_state_lake_data_yearly, {'model': 'cyan'}),
    path('rest/api/v1/<str:state>/lakes/info/', cyandata_restapi.getcyan_state_lake_info, {'model': 'cyan'}),
    path('rest/api/v1/<str:state>/lakes/info/<int:year>/', cyandata_restapi.getcyan_state_lake_info_yearly, {'model': 'cyan'}),
    path('rest/api/v1/lake/<str:lake>/', cyandata_restapi.getcyan_lake_data, {'model': 'cyan'}),
    path('rest/api/v1/lake/<str:lake>/<int:year>/', cyandata_restapi.getcyan_lake_data_yearly, {'model': 'cyan'}),
    path('rest/api/v1/lake/<str:lake>/info/', cyandata_restapi.getcyan_lake_info, {'model': 'cyan'}),
    path('rest/api/v1/lake/<str:lake>/info/<int:year>/', cyandata_restapi.getcyan_lake_info_yearly, {'model': 'cyan'}),
    path('rest/api/v1/lakes/info/', cyandata_restapi.getcyan_all_lake_info, {'model': 'cyan'}),
    path('rest/api/v1/lakes/info/<int:year>/', cyandata_restapi.getcyan_all_lake_info_yearly, {'model': 'cyan'}),
    path('map/rest/location/data/', cyan_rest.get_location_data),

    path('app/api/user/', web_app_api.login_user),
    path('app/api/user/register/', web_app_api.register_user),
    path('app/api/location/add/', web_app_api.add_location),
    path('app/api/location/delete/<str:user>/<str:_id>/', web_app_api.delete_location),
    path('app/api/location/edit/', web_app_api.edit_location)
]

# 404 Error view (file not found)
handler404 = views.file_not_found
# 500 Error view (server error)
handler500 = views.file_not_found
# 403 Error view (forbidden)
handler403 = views.file_not_found
