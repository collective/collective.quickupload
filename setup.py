# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
import sys


def read(*paths):
    return open(os.path.join(os.path.dirname(__file__), *paths)).read()

version = '1.11.1'

tests_require = [
    'plone.app.dexterity',
    'plone.app.testing',
    'mock',
    ]
if sys.version_info < (2, 7):
    tests_require.append('unittest2')

setup(name='collective.quickupload',
      version=version,
      description="Pure javascript files upload tool for Plone, with drag " +
                  "and drop, multi selection, and progress bar.",
      long_description="\n\n".join([
          read("README.rst"),
          read("docs", "HISTORY.rst"),
      ]),
      # Get more strings from
      # https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Topic :: Desktop Environment :: File Managers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Natural Language :: English",
          "Natural Language :: French",
          "Natural Language :: German",
          "Natural Language :: Spanish",
          "Natural Language :: Finnish",
          "Natural Language :: Italian",
          "Natural Language :: Norwegian",
          "Natural Language :: English",
          "Natural Language :: Portuguese (Brazilian)",
          "Natural Language :: Chinese (Simplified)",
          "Natural Language :: Chinese (Traditional)",
          "License :: OSI Approved :: GNU Affero General Public License v3"
      ],
      keywords='Plone Multiple Files Upload',
      author='jean-mat Grimaldi',
      author_email='jeanmat.grimaldi@gmail.com',
      url='http://plone.org/products/collective.quickupload',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'ua_parser',
      ],
      extras_require={
          'test': tests_require,
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
