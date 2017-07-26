from django.template.loader import render_to_string
from django.http import HttpResponse



def freqMap_page(request, model='cyan', header='none'):
    html = render_to_string('01epa_drupal_header.html', {})
    html += render_to_string('02epa_drupal_header_bluestripe_wide.html', {})

    html += render_to_string('cyan_freqMap_page.html', {})


    html += render_to_string('04ubertext_end_drupal.html', {})

    html += render_to_string('10epa_drupal_footer.html', {})


    response = HttpResponse()
    response.write(html)
    return response