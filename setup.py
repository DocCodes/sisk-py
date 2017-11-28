#!/usr/bin/env python3
from distutils.core import setup
setup(
   name = 'sisk-py',
   packages = ['sisk'],
   version = '0.3.0',
   description = 'A SISK12 API for Tyler Systems',
   author = 'Evan Young',
   url = 'https://github.com/DocCodes/sisk-py',
   download_url = 'https://github.com/DocCodes/sisk-py/archive/master.tar.gz',
   keywords = ['SISK', 'api', 'Tyler'],
   classifiers = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Programming Language :: Python :: 3.6',
      'Natural Language :: English'
   ],
   install_requires = [
      'requests',
   ],
   python_requires = '~=3.6'
)
