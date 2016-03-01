#!/usr/bin/env python3
from distutils.core import setup

setup(name='wikifolio-rss',
      version='0.0.1',
      description='RSS Feed transformation for wikifolio',
      author='Yves Fischer',
      author_email='yvesf+wikifolio@xapek.org',
      url='https://www.xapek.org/git/yvesf/wikifolio-rss',
      packages=['wikifolio'],
      scripts=['wikifolio-rss', 'wikifolio-plot-trades'],
      install_requires=['ll-xist'])
