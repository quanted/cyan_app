from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import redirect
import os
from django.conf import settings
from .links_left import ordered_list
from cyan_app import views



def description_page(request, model='cyan', header='none'):

    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(current_dir)

    header = views.header

    xx = render_to_string('cyan_text.txt')

    """ Returns the html of the references page for cyan. """
    html = render_to_string('01epa_drupal_header.html', {})
    html += render_to_string('02epa_drupal_header_bluestripe_onesidebar.html', {})
    html += render_to_string('03epa_drupal_section_title.html', {})

    html += render_to_string('04ubertext_start_index_drupal.html', {
        'TITLE': header + ' Overview',
        'TEXT_PARAGRAPH': xx})

    html += render_to_string('04ubertext_end_drupal.html', {})

    html += ordered_list(model)
    html += render_to_string('10epa_drupal_footer.html', {})


    response = HttpResponse()
    response.write(html)
    return response