# -*- coding: utf-8 -*-
try:
    # Python 2.6
    import unittest2 as unittest
except ImportError:
    # Python 2.7 has unittest2 integrated in unittest
    import unittest
from plone.testing import layered
from collective.quickupload import testing

import doctest

functional = [
    'installation.txt',
    'controlpanel.txt',
    'quickupload_view.txt',
    'portlet.txt',
]


def test_suite():

    tests = []

    for f in functional:
        tests.append(
            layered(
                doctest.DocFileSuite('tests/{0}'.format(f),
                                     package='collective.quickupload',
                                     optionflags=testing.OPTIONFLAGS,
                                     ),
                layer=testing.QUICKUPLOAD_FUNCTIONAL_TESTING,
            )
        )

    return unittest.TestSuite(tests)
