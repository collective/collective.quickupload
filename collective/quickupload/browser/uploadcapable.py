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

from types import UnicodeType
import transaction
from thread import allocate_lock
from AccessControl import Unauthorized
from ZODB.POSException import ConflictError
from Acquisition import aq_inner
from zope import interface
from zope import component
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from interfaces import IQuickUploadFileFactory
from zope.app.container.interfaces import INameChooser
from plone.i18n.normalizer.interfaces import IIDNormalizer

from Products.CMFPlone import utils as ploneutils
from Products.CMFCore import utils as cmfutils

from interfaces import IQuickUploadCapable

upload_lock = allocate_lock()


class QuickUploadCapableFileFactory(object):
    interface.implements(IQuickUploadFileFactory)
    component.adapts(IQuickUploadCapable)

    def __init__(self, context):
        self.context = aq_inner(context)

    def __call__(self, name, title, content_type, data, portal_type):

        context = aq_inner(self.context)
        charset = context.getCharset()
        filename = name
        name = name.decode(charset)
        error = ''
        result = {}
        result['success'] = None
        normalizer = component.getUtility(IIDNormalizer)
        chooser = INameChooser(self.context)
        newid = chooser.chooseName(normalizer.normalize(name), context)
        if not title :
            # try to split filenames because we don't want 
            # big titles without spaces
            title = name.split('.')[0].replace('_',' ').replace('-',' ')

        if newid in context.objectIds() :
            raise NameError, 'Object id %s always exist' %newid
        else :
            upload_lock.acquire()
            transaction.begin()
            try:
                context.invokeFactory(type_name=portal_type, id=newid, title=title)
            except Unauthorized : 
                error = u'serverErrorNoPermission'
            except ConflictError : 
                error = u'serverErrorZODBConflict'
            except :
                error = u'serverError'
            if not error :
                obj = getattr(context, newid)
                primaryField = obj.getPrimaryField()
                mutator = primaryField.getMutator(obj)
                mutator(data, content_type=content_type)
                # XXX when getting file through request.BODYFILE (XHR direct upload)
                # the filename is not inside the file
                # and the filename must be a string, not unicode
                # otherwise Archetypes raise an error (so we use filename and not name)
                if not obj.getFilename() :
                    obj.setFilename(filename)
                # XXX fix strange ATFile behavior with content_types
                if obj.getContentType() != content_type :
                    primaryField.setContentType(obj, content_type)
                obj.reindexObject()
            transaction.commit()
            upload_lock.release()
        
        result['error'] = error
        if not error :
            result['success'] = obj
        return result
