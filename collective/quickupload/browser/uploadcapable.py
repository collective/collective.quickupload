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
from thread import allocate_lock

import transaction
from AccessControl import Unauthorized
from ZODB.POSException import ConflictError
from Acquisition import aq_inner
from zope import interface
from zope import component
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.app.container.interfaces import INameChooser

from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.interfaces.base import IBaseObject
from Products.CMFPlone import utils as ploneutils
from Products.CMFCore import utils as cmfutils
from Products.CMFCore.utils import getToolByName

try:
    from zope.schema import getFieldsInOrder
    from plone.dexterity.interfaces import IDexterityContent
    from plone.rfc822.interfaces import IPrimaryField
    from plone.namedfile.interfaces import INamedFileField, INamedImageField, INamedBlobFileField, INamedBlobImageField
    from plone.namedfile.file import NamedFile, NamedImage, NamedBlobFile, NamedBlobImage
    HAS_DEXTERITY = True
except:
    HAS_DEXTERITY = False

from collective.quickupload import logger
from collective.quickupload.browser.interfaces import (
    IQuickUploadCapable, IQuickUploadFileFactory)


upload_lock = allocate_lock()

class QuickUploadCapableFileFactory(object):
    interface.implements(IQuickUploadFileFactory)
    component.adapts(IQuickUploadCapable)

    def __init__(self, context):
        self.context = aq_inner(context)

    def __call__(self, name, title, description, content_type, data, portal_type):
        context = aq_inner(self.context)
        charset = context.getCharset()
        filename = name
        name = name.decode(charset)
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
                        if IBaseObject.providedBy(obj): #@TODO: use adapters
                            primaryField = obj.getPrimaryField()
                            if primaryField is not None:
                                mutator = primaryField.getMutator(obj)
                                # mimetype arg works with blob files
                                mutator(data, content_type=content_type, mimetype=content_type)
                                # XXX when getting file through request.BODYFILE (XHR direct upload)
                                # the filename is not inside the file
                                # and the filename must be a string, not unicode
                                # otherwise Archetypes raise an error (so we use filename and not name)
                                if not obj.getFilename() :
                                    obj.setFilename(filename)

                                obj.reindexObject()
                                notify(ObjectInitializedEvent(obj))
                            else :
                                # some products remove the 'primary' attribute on ATFile or ATImage (which is very bad)
                                error = u'serverError'
                                logger.info("An error happens : impossible to get the primary field for file %s, rawdata can't be created",
                                            obj.absolute_url())
                        elif IDexterityContent.providedBy(obj):
                            ttool = getToolByName(self.context, 'portal_types')
                            ctype = ttool[obj.portal_type]
                            schema = ctype.lookupSchema()
                            fields = getFieldsInOrder(schema)
                            # @TODO: make it work with image fields
                            file_fields = [field for name, field in fields
                                           if INamedFileField.providedBy(field)
                                           or INamedImageField.providedBy(field)]
                            if len(file_fields) == 0:
                                error = u'serverError'
                                logger.info("An error happens : the dexterity content type %s has no file field, rawdata can't be created",
                                            obj.absolute_url())
                            for file_field in file_fields:
                                if IPrimaryField.providedBy(file_field):
                                    break
                            else:
                                # Primary field can't be set ttw,
                                # then, we take the first one
                                file_field = file_fields[0]

                            # TODO: use adapters
                            if INamedFileField.providedBy(file_field):
                                value = NamedFile(data=data,  contentType=content_type,
                                                  filename=unicode(filename))
                            elif INamedBlobFileField.providedBy(file_field):
                                value = NamedBlobFile(data=data,  contentType=content_type,
                                                  filename=unicode(filename))
                            elif INamedImageField.providedBy(file_field):
                                value = NamedImage(data=data,  contentType=content_type,
                                                  filename=unicode(file_field))
                            elif INamedBlobImageField.providedBy(field):
                                value = NamedBlobImage(data=data,  contentType=content_type,
                                                  filename=unicode(filename))

                            file_field.set(obj, value)
                            obj.reindexObject()
                            notify(ObjectInitializedEvent(obj))

                transaction.commit()

            finally:
                upload_lock.release()

        result['error'] = error
        if not error :
            result['success'] = obj
        return result
