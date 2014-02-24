# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.quickupload.browser.quickupload_settings import IQuickUploadControlPanel
from plone.app.layout.viewlets import common
from zope.component import getUtility


class QuickUploadViewlet(common.ViewletBase):

    def render(self):
        portal = getUtility(IPloneSiteRoot)
        try:
            qup_prefs = IQuickUploadControlPanel(portal)
        except AttributeError:
            return ""
        if not qup_prefs.show_upload_action:
            return ""
        return self.index()
