# -*- coding: utf-8 -*-  

from zope.testing import doctest
from unittest import TestSuite, main
from Testing import ZopeTestCase as ztc
from collective.quickupload.tests.base import QuickUploadTestCase



OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def test_suite():
    tests = [ 'installation.txt',
              'controlpanel.txt',
              'quickupload_view.txt',
              'portlet.txt',
             ]
    suite = TestSuite()
    for test in tests:
        suite.addTest(ztc.FunctionalDocFileSuite(test,
            optionflags=OPTIONFLAGS,
            package="collective.quickupload.tests",
            test_class=QuickUploadTestCase))
    return suite

