from collective.quickupload.testing import QUICKUPLOAD_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
import mock
import unittest2 as unittest


class TestCase(unittest.TestCase):

    layer = QUICKUPLOAD_FUNCTIONAL_TESTING

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

    def test_get_unique_filename(self):
        filename = 'my-file.jpg'
        portal = self.layer['portal']

        # Set already existing file
        setattr(portal, filename, object())

        from collective.quickupload.browser.uploadcapable import get_id_from_filename

        # Per default it does not return a unique value
        self.assertEqual(
            'my-file.jpg', get_id_from_filename(filename, portal))

        # Otherwise it returns a unique id if the id already exists
        self.assertEqual(
            'my-file-1.jpg',
            get_id_from_filename(filename, portal, unique=True))
