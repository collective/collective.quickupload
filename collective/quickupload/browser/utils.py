# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser import BrowserView
from collective.quickupload.browser.quickupload_settings import IQuickUploadControlPanel
from collective.quickupload.portlet.quickuploadportlet import IQuickUploadPortlet
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRetriever
from ua_parser import user_agent_parser
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
from zope.component import getUtility


class QuickuploadHelper(BrowserView):

    def show_quickupload_action(self):
        portal = getUtility(IPloneSiteRoot)
        qup_prefs = IQuickUploadControlPanel(portal)
        if not qup_prefs.show_upload_action:
            return False
        context_state = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name=u'plone_context_state')
        if not (
                context_state.is_default_page() or
                context_state.is_folderish()):
            return False
        # If the Quickuploader portlet is shown in the current context, don't
        # show the Upload action, since the portlet takes precedence
        portlet_managers = [
            x[1] for x in getUtilitiesFor(IPortletManager)
            if not x[0].startswith('plone.dashboard')
        ]
        for mgr in portlet_managers:
            retriever = getMultiAdapter((self.context, mgr), IPortletRetriever)
            portlets = retriever.getPortlets()
            for portlet in portlets:
                if IQuickUploadPortlet.providedBy(portlet["assignment"]):
                    return False
        return True


def can_dnd(user_agent):
    """All modern browsers are able to upload files"""
    result = user_agent_parser.Parse(user_agent)
    if result['user_agent']['family'] == u'IE':
        return int(result['user_agent']['major']) > 9
    return True
