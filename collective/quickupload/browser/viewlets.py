# -*- coding: utf-8 -*-
from collective.quickupload.browser.quickupload_settings import \
    IQuickUploadControlPanel
from plone.app.layout.viewlets import common
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class QuickUploadViewlet(common.ViewletBase):

    def render(self):
        try:
            registry = getUtility(IRegistry)
            qup_prefs = registry.forInterface(IQuickUploadControlPanel)
        except KeyError:
            return ""
        if not qup_prefs.show_upload_action:
            return ""
        return self.index()



