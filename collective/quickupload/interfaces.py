from zope.interface import Interface

class IQuickUploadFileSetter(Interface):
    """Adapter to set file data on a content
    """

    def set(self, data, content_type):
       """sets data of a content type on adaptated content
       @return an error code or '' if success
       """