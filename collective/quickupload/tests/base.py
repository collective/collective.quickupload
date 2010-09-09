# -*- coding: utf-8 -*-

"""Base class for quickupload test cases.
"""

import sys
from Products.PloneTestCase import PloneTestCase as ptc
from Products.Five.testbrowser import Browser
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.layer import PloneSite
from Testing import ZopeTestCase as ztc
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_product():
    """
    Set up the package and its dependencies.
    """    
    
    fiveconfigure.debug_mode = True
    import collective.quickupload
    zcml.load_config('configure.zcml',collective.quickupload)
    #fiveconfigure.debug_mode = False    
    ztc.installPackage('collective.quickupload')   

setup_product()
ptc.setupPloneSite(products=['collective.quickupload'])


class QuickUploadTestCase(ptc.FunctionalTestCase):
    """base test case with convenience methods for all tests""" 
    
    def afterSetUp(self):
        super(QuickUploadTestCase, self).afterSetUp()        
        self.browser = Browser()        
        self.uf = self.portal.acl_users
        self.uf.userFolderAddUser('root', 'secret', ['Manager'], [])
        self.uf.userFolderAddUser('contributor', 'secret', ['Member', 'Contributor'], [])        
        self.ptool = getToolByName(self.portal, 'portal_properties')    
    
    def loginAs(self, user, pwd):
        """points the browser to the login screen and logs in as specified user."""
        self.browser.open('http://nohost/plone/')
        self.browser.getLink('Log in').click()
        self.browser.getControl('Login Name').value = user
        self.browser.getControl('Password').value = pwd
        self.browser.getControl('Log in').click()

    def loginAsManager(self, user='root', pwd='secret'):
        """points the browser to the login screen and logs in as user root with Manager role."""
        self.loginAs(user='root', pwd='secret')
    
    def loginAsContibutor(self):
        """points the browser to the login screen and logs in as user contributor with Add Content permission."""
        self.loginAs(user='contributor', pwd='secret')        
    
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            # doctests don't play nicely with ipython
            try :
                iphook = sys.displayhook
                sys.displayhook = sys.__displayhook__
            except:
                pass    

        @classmethod
        def tearDown(cls):
            try :
                 sys.displayhook = iphook
            except:
                pass    
