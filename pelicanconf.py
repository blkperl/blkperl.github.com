#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = u'William Van Hevelingen'
SITENAME = u'puppet resource blog author=blkperl'
SITEURL = ''

TIMEZONE = 'America/Los_Angeles'

DEFAULT_LANG = u'en'

SOCIAL = (('twitter', 'http://twitter.com/pdx_blkperl'),
          ('github', 'http://github.com/blkperl'),)

DEFAULT_PAGINATION = 10

TWITTER_USERNAME='pdx_blkperl'

PLUGINS = [
    'pelican_gist',
]

STATIC_PATHS = ['images']
