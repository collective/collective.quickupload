import mock
import unittest2 as unittest


class TestCase(unittest.TestCase):

    def test_MissingExtension(self):
        from collective.quickupload.browser.uploadcapable import MissingExtension
        self.assertTrue(issubclass(MissingExtension, Exception))

    def test_get_id_from_filename__without_extension(self):
        context = mock.Mock()
        context.getCharset.return_value = 'utf-8'
        from collective.quickupload.browser.uploadcapable import MissingExtension
        from collective.quickupload.browser.uploadcapable import get_id_from_filename
        filename = 'FILENAME'
        self.assertRaises(
            MissingExtension,
            lambda: get_id_from_filename(filename, context)
        )
