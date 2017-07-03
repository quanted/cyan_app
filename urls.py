"""
Definition of urls for qed_cyan.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views

from .views import file_not_found
from .description import description_page
from .map import map_page
from .lakecomparison import lakecomparison_page
from .dashboard import dashboard_page
from .algorithms import algorithm_page
from .references import references_page
from .cyan_rest import get_location_data

# if settings.IS_PUBLIC:
urlpatterns = [
    # url(r'^$', views.cyan_landing_page),
    #front end urls
    url(r'^$', description_page, {'model': 'cyan'}),
    url(r'^map$', map_page, {'model': 'cyan'}),
    url(r'^lakecomparison$', lakecomparison_page, {'model': 'cyan'}),
    url(r'^dashboard$', dashboard_page, {'model': 'cyan'}),
    url(r'^algorithms$', algorithm_page, {'model': 'cyan'}),
    url(r'^references$', references_page, {'model': 'cyan'}),

    # url(r'^api$', rest.rest_page, {'model': 'cyan'}),
    # url(r'^swag$', views.getSwaggerJsonContent)

    # rest urls
    url(r'^rest/location/data$', get_location_data)
]
# else:
#     urlpatterns = [
#         #url(r'^api/', include('api.urls')),
#         #url(r'^rest/', include('REST.urls')),
#         url(r'^$', views.cyan_landing_page),
#         #url(r'^$', views.qed_splash_page_intranet),
#         # url(r'^admin/', include(admin.site.urls)),
#     ]

# 404 Error view (file not found)
handler404 = file_not_found
# 500 Error view (server error)
handler500 = file_not_found
# 403 Error view (forbidden)
handler403 = file_not_found