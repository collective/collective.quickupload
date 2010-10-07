# -*- coding: utf-8 -*-
#
# File: interfaces.py



from zope.interface import Interface
from zope.filerepresentation.interfaces import IFileFactory

class IQuickUploadCapable(Interface):
    """Any container/object which supports quick uploading
    """

class IQuickUploadFileFactory(IFileFactory):
    """used for QuickUploadFileFactory
    """

