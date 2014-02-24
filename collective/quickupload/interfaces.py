from zope.interface import Interface


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


# Copy of zope.filepresentation.interfaces.IFileFactory.
# We can't inherit from this because otherwise this adapter will be registered
# for IFileFactory too, and will be used for PUT requests (FTP/WebDAV)
class IDefaultFileFactory(Interface):

    def __call__(name, content_type, data):
        """Create a file

        where a file is an object with adapters to `IReadFile`
        and `IWriteFile`.

        The file `name`, content `type`, and `data` are provided to help
        create the object.
        """


class IQuickUploadFileFactory(IDefaultFileFactory):
    """used for QuickUploadFileFactory
    """


class IQuickUploadFileUpdater(IDefaultFileFactory):
    """used for QuickUploadFileFactory
    """
