#!/usr/bin/env python

from setuptools import setup


setup(name='aw-watcher-spotify',
      version='0.1',
      description='Spotify watcher for ActivityWatch',
      author='Erik Bjäreholt',
      author_email='erik@bjareho.lt',
      url='https://github.com/ActivityWatch/aw-watcher-spotify',
      packages=['aw_watcher_spotify'],
      install_requires=[
          'aw-client==0.2.0',
          'spotipy>=2.4.4',
      ],
      dependency_links=[
          'https://github.com/ActivityWatch/aw-client/tarball/master#egg=aw-client-0.2.0',
          'https://github.com/ActivityWatch/aw-core/tarball/master#egg=aw-core-0.2.0',
      ],
      entry_points={
          'console_scripts': ['aw-watcher-spotify = aw_watcher_spotify:main']
      },
      classifiers=[
          'Programming Language :: Python :: 3'
      ])
