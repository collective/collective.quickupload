# -*- coding: utf-8 -*-
from plone.testing import layered
from collective.quickupload import testing

import doctest
import unittest2 as unittest

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
