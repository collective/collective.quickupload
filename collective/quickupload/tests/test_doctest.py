from zope.testing import doctest
from unittest import TestSuite, main
from Testing import ZopeTestCase as ztc

from collective.quickupload.tests import base


OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def test_suite():
    tests = [ 'installation.txt',
              'controlpanel.txt',
              'ckeditor_jsconfig.txt',
              'uninstall.txt',
              'widget.txt',
              'transform_uids.txt',
             ]
    suite = TestSuite()
    for test in tests:
        suite.addTest(ztc.FunctionalDocFileSuite(test,
            optionflags=OPTIONFLAGS,
            package="collective.quickupload.tests",
            test_class=base.FunctionalTestCase))
    return suite


