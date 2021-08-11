# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.quickupload.browser.quickupload_settings import \
    IQuickUploadControlPanel
from plone.app.layout.viewlets import common
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class QuickUploadViewlet(common.ViewletBase):

    def render(self):
        portal = getUtility(IPloneSiteRoot)
        try:
            registry = getUtility(IRegistry)
            qup_prefs = registry.forInterface(IQuickUploadControlPanel)
        except AttributeError:
            return ""
        if not qup_prefs.show_upload_action:
            return ""
        return self.index()
