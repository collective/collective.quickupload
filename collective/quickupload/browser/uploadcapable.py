# -*- coding: utf-8 -*-
#
#
# Copyright (c) InQuant GmbH
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from thread import allocate_lock

import transaction
from AccessControl import Unauthorized
from ZODB.POSException import ConflictError
from Acquisition import aq_inner
from zope import interface
from zope import component
from zope.app.container.interfaces import INameChooser

from plone.i18n.normalizer.interfaces import IIDNormalizer

from collective.quickupload import logger
from collective.quickupload.browser.interfaces import (
    IQuickUploadCapable, IQuickUploadFileFactory)
from collective.quickupload.interfaces import IQuickUploadFileSetter

upload_lock = allocate_lock()

class QuickUploadCapableFileFactory(object):
    interface.implements(IQuickUploadFileFactory)
    component.adapts(IQuickUploadCapable)

    def __init__(self, context):
        self.context = aq_inner(context)

    def __call__(self, filename, title, description, content_type, data, portal_type):
        context = aq_inner(self.context)
        charset = context.getCharset()
        name = filename.decode(charset)
        error = ''
        result = {}
        result['success'] = None
        normalizer = component.getUtility(IIDNormalizer)
        chooser = INameChooser(self.context)
        # normalize all filename but dots
        normalized = ".".join([normalizer.normalize(n) for n in name.split('.')])
        newid = chooser.chooseName(normalized, context)

        # consolidation because it's different upon Plone versions
        newid = newid.replace('_','-').replace(' ','-').lower()
        if not title :
            # try to split filenames because we don't want
            # big titles without spaces
            title = name.split('.')[0].replace('_',' ').replace('-',' ')
        if newid in context.objectIds() :
            # only here for flashupload method since a check_id is done
            # in standard uploader - see also XXX in quick_upload.py
            raise NameError, 'Object id %s already exists' %newid
        else :
            upload_lock.acquire()
            try:
                transaction.begin()
                try:
                    context.invokeFactory(type_name=portal_type, id=newid, title=title, description=description)
                except Unauthorized :
                    error = u'serverErrorNoPermission'
                except ConflictError :
                    # rare with xhr upload / happens sometimes with flashupload
                    error = u'serverErrorZODBConflict'
                except Exception, e:
                    error = u'serverError'
                    logger.exception(e)

                if error:
                    error = u'serverError'
                    logger.info("An error happens with setId from filename, "
                                "the file has been created with a bad id, "
                                "can't find %s", newid)
                else:
                    obj = getattr(context, newid)
                    if obj:
                        error = IQuickUploadFileSetter(obj).set(data, filename, content_type)

                #@TODO : rollback if there has been an error
                transaction.commit()
            finally:
                upload_lock.release()

        result['error'] = error
        if not error :
            result['success'] = obj
        return result