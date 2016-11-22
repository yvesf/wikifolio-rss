#!/usr/bin/env python3
from distutils.core import setup

setup(name='wikifolio-rss',
      version='0.0.2',
      description='RSS Feed transformation for wikifolio',
      author='Yves Fischer',
      author_email='yvesf+wikifolio@xapek.org',
      url='https://github.com/yvesf/wikifolio-rss',
      packages=['wikifolio'],
      scripts=['wikifolio-comments-rss', 'wikifolio-trades-rss'],
      install_requires=['ll-xist', 'lxml'])
