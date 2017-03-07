from django.template.loader import render_to_string
from collections import OrderedDict
from django.shortcuts import redirect


# 03ubertext_links_left:
def ordered_list(model=None, page=None):
    link_dict = OrderedDict([
        ('Model', OrderedDict([
                ('Cyan', 'cyan'),
            ])
        ),
        ('Documentation', OrderedDict([
                ('API Documentation', '/qedinternal.epa.gov/cyan/rest'),
                ('Source Code', '/github.com/quanted/qed_cyan')
            ])
        )
    ])

    #return render_to_string('hwbi/03ubertext_links_left_drupal.html', {
    return render_to_string('03cyan_links_left_drupal.html', {
        'LINK_DICT': link_dict,
        'MODEL': model,
        'PAGE': page
    })