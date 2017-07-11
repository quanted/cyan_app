from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import redirect
import os
from django.conf import settings
from . import links_left
from cyan_app import views



def lakecomparison_page(request, model='cyan', header='none'):

    """ Returns the html of the references page for cyan. """
    html = render_to_string('01epa_drupal_header.html', {})
    html += render_to_string('02epa_drupal_header_bluestripe_wide.html', {})

    html += render_to_string('cyan_lake_compare.html', {})

    html += render_to_string('04ubertext_end_drupal.html', {})

    html += render_to_string('10epa_drupal_footer.html', {})


    response = HttpResponse()
    response.write(html)
    return response