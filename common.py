#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Common definitions for LastFM's Distributed Crawler."""


# Ammount of user pages to retrieve during a single FINDUSERS action
FINDUSERS_PAGE_COUNT = 10

# List of valid gender strings to be sent in a FINDUSERS command
FINDUSERS_VALID_GENDERS = 'mf'

# Separator used in page-users lists
FINDUSERS_SEPARATOR = "\x00"

FINDUSERS_URL_TEMPLATE = 'http://www.lastfm.com.br/users?gender=%s&age_min=&age_max=&country=&bio=&taste=&m=browse&&page=%d'

