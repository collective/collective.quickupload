from Products.CMFCore.utils import getToolByName
from collective.quickupload import logger
from collective.quickupload.interfaces import IQuickUploadFileSetter
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemataForType
from plone.namedfile.file import NamedFile
from plone.namedfile.file import NamedImage
from plone.namedfile.interfaces import INamedFileField
from plone.namedfile.interfaces import INamedImageField
from plone.rfc822.interfaces import IPrimaryFieldInfo
from zope.component import adapts
from zope.interface import implements
from zope.schema import getFieldsInOrder

try:
    from plone.namedfile.file import NamedBlobFile
    from plone.namedfile.file import NamedBlobImage
    from plone.namedfile.interfaces import INamedBlobFileField
    from plone.namedfile.interfaces import INamedBlobImageField
    HAVE_BLOBS = True
except:
    HAVE_BLOBS = False


def getAllFields(portal_type):
    schemas = iterSchemataForType(portal_type)
    fields = []
    for schema in schemas:
        fields += getFieldsInOrder(schema)
    return fields


class DexterityFileSetter(object):
    implements(IQuickUploadFileSetter)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    def set(self, data, filename, content_type):
        error = ''
        obj = self.context
        ttool = getToolByName(obj, 'portal_types')
        ctype = ttool[obj.portal_type]
        fields = getAllFields(ctype)
        try:
            file_field = IPrimaryFieldInfo(obj).field
        except TypeError:
            file_field = None
        if file_field is None:
            file_fields = [field for name, field in fields
                           if INamedFileField.providedBy(field)
                           or INamedImageField.providedBy(field)]
            if len(file_fields) == 0:
                error = u'serverError'
                logger.info("An error happens : the dexterity content type %s "
                            "has no file field, rawdata can't be created",
                            obj.absolute_url())
            file_field = file_fields[0]

        # TODO: use adapters
        if HAVE_BLOBS and INamedBlobImageField.providedBy(file_field):
            value = NamedBlobImage(
                data=data, contentType=content_type,
                filename=unicode(filename, 'utf-8')
            )
        elif HAVE_BLOBS and INamedBlobFileField.providedBy(file_field):
            value = NamedBlobFile(
                data=data, contentType=content_type,
                filename=unicode(filename, 'utf-8')
            )
        elif INamedImageField.providedBy(file_field):
            value = NamedImage(
                data=data, contentType=content_type,
                filename=unicode(filename, 'utf-8')
            )
        elif INamedFileField.providedBy(file_field):
            value = NamedFile(
                data=data, contentType=content_type,
                filename=unicode(filename, 'utf-8')
            )
        else:
            value = data  # When used by a text field for Document FTI, for example

        # Should be replaced by the correct setattr (behaviour) as in dexterity.utils.createContent
        file_field.set(obj, value)

        return error
