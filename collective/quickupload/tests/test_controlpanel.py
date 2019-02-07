# -*- coding: utf-8 -*-
try:
    # Python 2.6
    import unittest2 as unittest
except ImportError:
    # Python 2.7 has unittest2 integrated in unittest
    import unittest

from zope.component import getMultiAdapter
from Products.CMFPlone.utils import getFSVersionTuple

from plone.app.testing import TEST_USER_ID
from plone.app.testing import logout
from plone.app.testing import setRoles

from collective.quickupload.testing import QUICKUPLOAD_INTEGRATION_TESTING


class ControlPanelTest(unittest.TestCase):

    layer = QUICKUPLOAD_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.cp = getattr(self.portal, 'portal_controlpanel')

    def test_installed(self):
        # entry is in the control panel
        installed = [a.getAction(self)['id'] for a in self.cp.listActions()]
        self.assertIn('QuickUpload', installed)

    @unittest.skipIf(getFSVersionTuple() < (4, 3,),
                     'uninstallation does not seem to work in plone 4.2.')
    def test_uninstalled(self):
        setup_tool = getattr(self.portal, 'portal_setup')
        setup_tool.runAllImportStepsFromProfile(
            'profile-collective.quickupload:uninstall')

        # entry is removed from the control panel
        installed = [a.getAction(self)['id'] for a in self.cp.listActions()]
        self.assertNotIn('QuickUpload', installed)

    def test_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name='quickupload-controlpanel')
        view = view.__of__(self.portal)
        self.failUnless(view())

    def test_view_protected(self):
        # view can not be accessed by anonymous users
        from AccessControl import Unauthorized
        logout()
        self.assertRaises(Unauthorized,
                          self.portal.restrictedTraverse,
                          '@@quickupload-controlpanel')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
