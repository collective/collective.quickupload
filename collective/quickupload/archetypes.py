from Products.Archetypes.interfaces import IBaseObject
from collective.quickupload import logger
from collective.quickupload.interfaces import IQuickUploadFileSetter
from zope.component import adapts
from zope.interface import implements


class ArchetypesFileSetter(object):
    implements(IQuickUploadFileSetter)
    adapts(IBaseObject)

    def __init__(self, context):
        self.context = context

    def set(self, data, filename, content_type):
        error = ''
        obj = self.context
        primaryField = obj.getPrimaryField()
        if primaryField is not None:
            mutator = primaryField.getMutator(obj)
            # mimetype arg works with blob files
            mutator(data, content_type=content_type, mimetype=content_type)
            if not obj.getFilename():
                obj.setFilename(filename)

            obj.reindexObject()
        else:
            # some products remove the 'primary' attribute on ATFile or ATImage
            # (which is very bad)
            error = u'serverError'
            logger.info(
                "An error happens : impossible to get the primary field "
                "for file %s, rawdata can't be created",
                obj.absolute_url()
            )

        return error
