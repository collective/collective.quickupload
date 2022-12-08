import six
from Products.CMFCore.utils import getToolByName
from collective.quickupload import logger
from collective.quickupload.interfaces import IQuickUploadFileSetter
from plone.app.textfield import RichTextValue
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemataForType
from plone.namedfile.file import NamedFile
from plone.namedfile.file import NamedImage
from plone.namedfile.interfaces import INamedFileField
from plone.namedfile.interfaces import INamedImageField
from plone.rfc822.interfaces import IPrimaryFieldInfo
from zope.component import adapter
from zope.interface import implementer
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


@implementer(IQuickUploadFileSetter)
@adapter(IDexterityContent)
class DexterityFileSetter(object):

    def __init__(self, context):
        self.context = context

    def set(self, data, filename, content_type):
        if isinstance(filename, six.binary_type):
            filename = filename.decode('utf-8')
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

        # TODO: use adapters including failing when field type is not implemented
        if HAVE_BLOBS and INamedBlobImageField.providedBy(file_field):
            value = NamedBlobImage(
                data=data, contentType=content_type,
                filename=filename
            )
        elif HAVE_BLOBS and INamedBlobFileField.providedBy(file_field):
            value = NamedBlobFile(
                data=data, contentType=content_type,
                filename=filename
            )
        elif INamedImageField.providedBy(file_field):
            value = NamedImage(
                data=data, contentType=content_type,
                filename=filename
            )
        elif INamedFileField.providedBy(file_field):
            value = NamedFile(
                data=data, contentType=content_type,
                filename=filename
            )
        else:
            # When used by a text field for Document FTI, for example
            value = RichTextValue(data, mimeType=content_type, outputMimeType=content_type, encoding="utf-8")


        # Should be replaced by the correct setattr (behaviour) as in dexterity.utils.createContent
        file_field.set(obj, value)

        return error
