# -*- coding: utf-8 -*-

from plone.app.layout.viewlets import common


class QuickUploadViewlet(common.ViewletBase):

    def render(self):
        return self.index()
