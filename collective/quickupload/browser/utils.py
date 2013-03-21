# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter


class QuickuploadHelper(BrowserView):

    def show_quickupload_action(self):
        context_state = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name=u'plone_context_state')
        show = context_state.is_default_page() or context_state.is_folderish()
        return show
