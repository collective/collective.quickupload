# -*- coding: utf-8 -*-
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import login
from plone.app.testing import setRoles

import doctest


class QuickUploadLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.quickupload
        self.loadZCML(package=collective.quickupload)
        try:
            import plone.namedfile
            self.loadZCML(package=plone.namedfile)
        except:
            pass

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'collective.quickupload:default')

        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        portal.invokeFactory('Folder', 'test-folder', title=u"Test Folder")
        setRoles(portal, TEST_USER_ID, ['Member'])


QUICKUPLOAD_FIXTURE = QuickUploadLayer()

QUICKUPLOAD_INTEGRATION_TESTING = IntegrationTesting(
    bases=(QUICKUPLOAD_FIXTURE,),
    name='collective.quickupload:Integration',
)

QUICKUPLOAD_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(QUICKUPLOAD_FIXTURE,),
    name='collective.quickupload:Functional',
)

OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
