from Products.CMFCore.utils import getToolByName
from collective.quickupload import logger
from collective.quickupload.interfaces import IQuickUploadFileSetter
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile.file import NamedFile
from plone.namedfile.file import NamedImage
from plone.namedfile.interfaces import INamedFileField
from plone.namedfile.interfaces import INamedImageField
from plone.rfc822.interfaces import IPrimaryField
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
        schema = ctype.lookupSchema()
        fields = getFieldsInOrder(schema)
        file_fields = [field for name, field in fields
                       if INamedFileField.providedBy(field)
                       or INamedImageField.providedBy(field)]
        if len(file_fields) == 0:
            error = u'serverError'
            logger.info("An error happens : the dexterity content type %s "
                        "has no file field, rawdata can't be created",
                        obj.absolute_url())
        for file_field in file_fields:
            if IPrimaryField.providedBy(file_field):
                break
        else:
            # Primary field can't be set ttw,
            # then, we take the first one
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

        file_field.set(obj, value)
        return error
