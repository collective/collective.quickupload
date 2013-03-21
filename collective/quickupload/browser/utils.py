# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser import BrowserView
from collective.quickupload.browser.quickupload_settings import \
    IQuickUploadControlPanel
from collective.quickupload.portlet.quickuploadportlet import \
    IQuickUploadPortlet
from plone.app.portlets.utils import assignment_mapping_from_key
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import IPortletManager
from zope.component import getMultiAdapter, getUtility, getUtilitiesFor


class QuickuploadHelper(BrowserView):

    def show_quickupload_action(self):
        portal = getUtility(IPloneSiteRoot)
        qup_prefs = IQuickUploadControlPanel(portal)
        if not qup_prefs.show_upload_action:
            return False
        context_state = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name=u'plone_context_state')
        # If the Quickuploader portlet is shown in the current context, don't
        # show the Upload action, since the portlet takes precedence
        portlet_manager_names = [
            x[0] for x in getUtilitiesFor(IPortletManager)
            if not x[0].startswith('plone.dashboard')
        ]
        path = '/'.join(self.context.getPhysicalPath())
        for name in portlet_manager_names:
            portlets = assignment_mapping_from_key(
                self.context, name, CONTEXT_CATEGORY, path).values()
            for portlet in portlets:
                if IQuickUploadPortlet.providedBy(portlet):
                    return False

        return context_state.is_default_page() or context_state.is_folderish()
