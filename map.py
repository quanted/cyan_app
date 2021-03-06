from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import redirect
import os
from django.conf import settings
from .links_left import ordered_list
from cyan_app import views



def map_page(request, model='cyan', header='none'):
    header = views.header
    x = render_to_string('cyan_map_page_pythoncall.html')

    """ Returns the html of the references page for cyan. """
    html = render_to_string('01epa_drupal_header.html', {})
    html += render_to_string('02epa_drupal_header_bluestripe_onesidebar.html', {})
    html += render_to_string('03epa_drupal_section_title.html', {})

    html += render_to_string('04ubertext_start_index_drupal.html', {
        'TITLE': header + ' Map',
        'TEXT_PARAGRAPH': x})

    html += render_to_string('04ubertext_end_drupal.html', {})

    html += ordered_list(model, 'map')
    html += render_to_string('10epa_drupal_footer.html', {})


    response = HttpResponse()
    response.write(html)
    return response