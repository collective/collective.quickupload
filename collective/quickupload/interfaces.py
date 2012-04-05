from zope.interface import Interface
from zope.filerepresentation.interfaces import IFileFactory


class IQuickUploadFileSetter(Interface):
    """Adapter to set file data on a content
    """

    def set(self, data, content_type):
       """sets data of a content type on adaptated content
       @return an error code or '' if success
       """

class IQuickUploadCapable(Interface):
    """Any container/object which supports quick uploading
    """

class IQuickUploadNotCapable(Interface):
    """Any container/object which NEVER supports quick uploading
    """

class IQuickUploadFileFactory(IFileFactory):
    """used for QuickUploadFileFactory
    """


class IQuickUploadFileUpdater(IFileFactory):
    """used for QuickUploadFileFactory
    """