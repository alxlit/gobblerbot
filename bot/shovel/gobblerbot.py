#!/usr/bin/env python

from shovel import task

@task
def update_templates():
    """(Not yet implemented)."""
    templates = [
        'buildings.mustache',
        'residence_hall.mustache'
    ]

    out = os.path.abspath(os.path.dirname(__file__) + '../templates/')

