"""
Definition of urls for qed_cyan.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views

import views
import description
import dashboard
# import stream
import algorithms
import references
import links_left

# if settings.IS_PUBLIC:
urlpatterns = [
    # url(r'^$', views.cyan_landing_page),
    #front end urls
    url(r'^$', description.description_page, {'model': 'cyan'}),
    url(r'^dashboard$', dashboard.dashboard_page, {'model': 'cyan'}),
    url(r'^algorithms$', algorithms.algorithm_page, {'model': 'cyan'}),
    url(r'^references$', references.references_page, {'model': 'cyan'}),
    # url(r'^api$', rest.rest_page, {'model': 'cyan'}),
    # url(r'^swag$', views.getSwaggerJsonContent)
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
handler404 = views.file_not_found
# 500 Error view (server error)
handler500 = views.file_not_found
# 403 Error view (forbidden)
handler403 = views.file_not_found