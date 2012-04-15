#!/usr/bin/env python

from shovel import task
from bot.db import db
from bot.log import logger
import csv
from difflib import get_close_matches
import os
import urllib
import re

MASTER_LIST = 'CSV.DataFile'
MASTER_LIST_URL = 'http://www.cdcd.vt.edu/MBlist/' + MASTER_LIST

_numbers = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
            'nine', 'ten']

_numbers_words = {}

for i, word in enumerate(_numbers):
    _numbers_words[word] = i + 1

def fuzzy_find(field, value):
    buildings = {}

    for bldg in db.buildings.find():
        buildings[bldg[field]] = bldg

    matches = get_close_matches(value, buildings.keys())
    return [buildings[match] for match in matches]

@task
def create_articles():
    """(Not yet implemented)."""
    pass

@task
def create_tables():
    """(Not yet implemented)."""
    pass

@task
def populate():
    """Populate the buildings collection using Virginia Tech's master list."""
    if not os.path.exists(MASTER_LIST):
        update_master_list()

    reader = csv.reader(open(MASTER_LIST, newline=''), delimeter=',',
                        quotechar='"')

    keys = ['id', 'name', 'abbreviation', 'status', 'address', 'campus', 'city']
    keys = enumerate(keys)

    for i, row in enumerate(reader):
        if len(row) != 7:
            logger.debug('Invalid row %d: %s' % (i, row))
            continue

        data = {}

        for i, key in keys:
            data[key] = row[i]

        # Existing record
        bldg = db.buildings.find_one({'id': data['id']}) or {}

        data['type'] = 'building'

        # Format the building name
        m = re.match(r'([\w\s-]+)(?:\[(.+)\])?', data['name']).groups()

        data['name'], data['usage'] = m

        if data['address'].find('campus') >= 0 and data['campus'] == '':
            # For whatever reason the campus and address are sometimes flipped
            # around when there's no address
            data['campus'], data['address'] = data['address'], ''

        bldg.update(data)

        # Update record
        db.buildings.save(bldg)

@task
def scrape_about():
    """Scrape the "about" pages from the Virginia Tech website."""
    URL = 'http://www.vt.edu/about/buildings/%s.html'

    # Load the index
    html = lxml.html.parse(urllib.urlopen(URL % 'index')).getroot()

    for anchor in html.cssselect('#vt_body_col li a'):
        slug, name = anchor.get('href'), anchor.text_content()

        # Extract page slug (filename without the extension)
        slug = slug[slug.rfind('/') + 1: -5]

        try:
            bldg = fuzzy_find('name', slug)[0]
            bldg['about_slug'] = slug
        except:
            logger.warning("Couldn't find matching building for '%s'." % slug)
            continue

        db.buildings.save(bldg)

    scrapers = {
        'abbrev':    (r'Abbreviation:\s+([A-Z0-9\s]+)'),
        'address':   (r'Address:\s+(\w\s+)\s+\|'),
        'built':     (r'Originally\s+Built:\s+([0-9]{4})\s+\|'),
        'floors':    (r'(%s)\s+floors' % '|'.join(range(1, 11)), re.I),
        'grid':      (r'Map\s+Grid:\s+([A-Z]-[0-9])'),
        'latitude':  (r'Latitude:\s+(\-?[0-9]+\.[0-9]+)'),
        'longitude': (r'Longitude:\s+(\-?[0-9]+\.[0-9]+)'),
    }

    for bldg in db.buildings.find({ 'about_slug': { '$exists': True } }):
        try:
            html = urllib.urlopen(URL % bldg['about_slug'])
            html = lxml.parse(html).getroot()
        except:
            logger.warning('The about page for %s is malformed.' % bldg['id'])
            continue

        for paragraph in html.cssselect('#vt_body_col > p'):
            text = paragraph.text_content()

            for key, regex in scrapers:
                match = re.compile(*regex).search(text)

                if match:
                    bldg[key] = match.group(1).strip()

        db.buildings.save(bldg)

@task
def scrape_cdcd():
    """Scrape information for each building from the CDCD site (cdcd.vt.edu)."""
    URL = 'http://www.cdcd.vt.edu/Building.Info/%s.html'

    scrapers = {
        'abbrev':      (r'Abbreviation:\s+([A-Z0-9\s]+)'),
        'address':     (r'Address:\s(.+)'),
        'built':       (r'Original\s+Construction\s+Year:\s+([0-9]{4})'),
        'gross_sq_ft': (r'\(GSF\):\s([0-9,]+)'),
    }

    for bldg in db.buildings.find():
        try:
            html = urllib.urlopen(URI % bldg['id'])
            html = lxml.parse(html).getroot()
        except:
            logger.warning('The CDCD page for %s is malformed.' % bldg['id'])
            continue

        for paragraph in html.cssselect('#vt_body_col > p'):
            text = paragraph.text_content()

            for key, regex in scrapers:
                match = re.compile(*regex).search(text)

                if match:
                    bldg[key] = match.group(1).strip()

        db.buildings.save(bldg)

@task
def scrape_cdcd_departments():
    """(Not yet implemented). Get the list of departments for each building
    from the CDCD site (cdcd.vt.edu)."""
    URL = 'http://www.cdcd.vt.edu/Building.Info/Info.dep/%s.DEP'

    for bldg in db.buildings.find():
        pass

@task
def scrape_housing():
    """Scrape the housing site (housing.vt.edu) for each building to determine
    whether it's a residence hall."""
    URL = 'http://www.housing.vt.edu/halls/%s.php'

    # Load the index
    html = lxml.html.parse(urllib.urlopen(URL % 'index')).getroot()

    for anchor in html.cssselect('#content_container_middle li a'):
        slug = anchor.get('href')
        text = anchor.text_content()

        try:
            bldg = fuzzy_find('name', text)[0]
            bldg.update({ 'housing_slug': slug, 'type': 'residence_hall' })
        except:
            logger.warning("Couldn't find matching building for '%s'." % slug)
            continue

        db.buildings.save(bldg)

@task
def update_master_list():
    """Re-download the master buildings list."""
    try:
        os.remove(MASTER_LIST)
    except:
        pass

    data = urllib.urlopen(MASTER_LIST_URL).decode('utf-8')

    f = open(MASTER_LIST, 'w')
    f.write(data)
    f.close()
