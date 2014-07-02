import unittest2 as unittest
from collective.quickupload.testing import QUICKUPLOAD_INTEGRATION_TESTING
import os.path
from collective.quickupload.browser.quick_upload import get_content_type
from Products.CMFCore.utils import getToolByName
from ZPublisher.HTTPRequest import FileUpload
import cgi

class TestMimetypes(unittest.TestCase):

    layer = QUICKUPLOAD_INTEGRATION_TESTING
    
    def setUp(self):
        self.portal = self.layer['portal']
        file_ = open("%s/testfile_mimetypes.txt" % os.path.split(__file__)[0], 'r')
        self.file_data = file_.read()
        fieldstorage = cgi.FieldStorage()
        fieldstorage.file = file_
        fieldstorage.filename = 'testfile_mimetypes.txt'
        self.fileupload = FileUpload(fieldstorage)
        mtr = getToolByName(self.portal, 'mimetypes_registry')
        mtr.manage_addMimeType('Only globs mimetype', ['application/x-only-glob'], [], 'application.png', globs=['*.onlyglob'])
        mtr.manage_addMimeType('Only extension mimetype', ['application/x-only-ext'], ['onlyext'], 'application.png')
    
    def test_only_globs(self):
        content_type = get_content_type(self.portal, self.file_data, 'dummy.onlyglob')
        self.assertEqual('application/x-only-glob', content_type)

    def test_only_ext(self):
        content_type = get_content_type(self.portal, self.file_data, 'dummy.onlyext')
        self.assertEqual('application/x-only-ext', content_type)
    
    def test_recognized_by_python(self):
        content_type = get_content_type(self.portal, self.file_data, 'dummy.txt')
        self.assertEqual('text/plain', content_type)

    def test_fileupload_instance(self):
        content_type = get_content_type(self.portal, self.fileupload, 'dummy.txt')
        self.assertEqual('text/plain', content_type)
