try:
    # Python 2.6
    import unittest2 as unittest
except ImportError:
    # Python 2.7 has unittest2 integrated in unittest
    import unittest
from collective.quickupload.browser.uploadcapable import QuickUploadCapableFileFactory
from collective.quickupload.browser.uploadcapable import QuickUploadCapableFileUpdater
from collective.quickupload.interfaces import IQuickUploadFileFactory
from collective.quickupload.interfaces import IQuickUploadFileUpdater
from collective.quickupload.testing import QUICKUPLOAD_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFPlone.interfaces import IPloneSiteRoot
from StringIO import StringIO
from zope.component import getGlobalSiteManager
from zope.publisher.browser import TestRequest
import json
import transaction


class TemporaryAdapterRegistration(object):
    """Context manager to temporarily register an adapter."""

    def __init__(self, factory, required=None, provided=None, name=u''):
        self.gsm = getGlobalSiteManager()
        self.factory = factory
        self.required = required
        self.provided = provided
        self.name = name

    def __enter__(self):
        self.gsm.registerAdapter(
            self.factory, required=self.required, provided=self.provided,
            name=self.name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        is_unregistered = self.gsm.unregisterAdapter(
            self.factory, required=self.required, provided=self.provided,
            name=self.name)
        if not is_unregistered:
            raise RuntimeError("Could not unregister adapter.")
        return False


class TestCase(unittest.TestCase):

    layer = QUICKUPLOAD_FUNCTIONAL_TESTING

    def _upload_file(self, filename, title=None, description=None,
                     bodyfile=None):
        from collective.quickupload.browser.quick_upload import QuickUploadFile
        portal = self.layer['portal']
        request = TestRequest()
        # We need a RESPONSE object.
        request.RESPONSE = request._createResponse()
        # Signal that this is an ajax upload:
        request.HTTP_X_REQUESTED_WITH = 'XHR'
        # Set file name:
        request.HTTP_X_FILE_NAME = filename
        request.BODYFILE = bodyfile or StringIO('dummy file content')
        if title is not None:
            request.form['title'] = title
        if description is not None:
            request.form['description'] = description
        view = QuickUploadFile(portal, request)
        return json.loads(view())

    def test_upload_file_simple(self):
        filename = 'my-file.jpg'
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        result = self._upload_file(filename)
        self.assertEqual(result.get('success'), True)
        self.assertFalse(result.get('error'))
        self.assertEqual(result.get('name'), filename)
        self.assertEqual(result.get('title'), 'my file')
        self.assertTrue(filename in portal)
        image = portal[filename]
        self.assertEqual(image.Title(), 'my file')
        self.assertEqual(result.get('uid'), image.UID())

    def test_upload_file_unauthorized(self):
        filename = 'my-file.jpg'
        portal = self.layer['portal']
        result = self._upload_file(filename)
        self.assertEqual(result.get('error'), 'serverErrorNoPermission')
        self.assertFalse(result.get('success'))
        self.assertFalse(filename in portal)

    def test_upload_file_abort_returns_empty_error(self):
        filename = 'cheese.txt'
        result = self._upload_file(filename, bodyfile=object())
        self.assertEqual({u'error': u'emptyError'}, result)

    def test_upload_empty_file_returns_empty_error(self):
        filename = 'cheese.txt'
        result = self._upload_file(filename, bodyfile=StringIO(''))
        self.assertEqual({u'error': u'emptyError'}, result)

    def test_upload_file_read_error_returns_server_error(self):
        class FailingFile(object):
            def read():
                raise Exception("oops")

        filename = 'parrot.txt'
        result = self._upload_file(filename, bodyfile=FailingFile())
        self.assertEqual({u'error': u'serverError'}, result)

    def test_upload_file_raises_missing_extension_for_invalid_filenames(self):
        filename = 'ni'
        result = self._upload_file(filename)
        self.assertEqual({u'error': u'missingExtension'}, result)

    def test_file_updater_exception_returns_server_error(self):
        class FailingFileUpdater(QuickUploadCapableFileUpdater):
            def __call__(self, *args, **kwargs):
                raise Exception("duh!")

        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        props = portal.portal_properties.quickupload_properties
        props._updateProperty('object_unique_id', False)
        props._updateProperty('object_override', True)
        transaction.commit()

        with TemporaryAdapterRegistration(FailingFileUpdater,
                                          required=(IPloneSiteRoot,),
                                          provided=IQuickUploadFileUpdater):
            filename = 'qux.txt'
            result = self._upload_file(filename)
            # upload again, force update
            result = self._upload_file(filename)
            self.assertEqual({u'error': u'serverError'}, result)

    def test_file_updater_error_returns_custom_error(self):
        class ErrorFileUpdater(QuickUploadCapableFileUpdater):
            def __call__(self, *args, **kwargs):
                return {"error": "It's stone dead", "success": None}

        portal = self.layer["portal"]
        setRoles(portal, TEST_USER_ID, ("Manager",))
        props = portal.portal_properties.quickupload_properties
        props._updateProperty("object_unique_id", False)
        props._updateProperty("object_override", True)
        transaction.commit()

        with TemporaryAdapterRegistration(ErrorFileUpdater,
                                          required=(IPloneSiteRoot,),
                                          provided=IQuickUploadFileUpdater):
            filename = "qux.txt"
            result = self._upload_file(filename)
            # upload again, force update
            result = self._upload_file(filename)
            self.assertEqual({u"error": u"It's stone dead"}, result)

    def test_file_factory_exception_returns_server_error(self):
        class FailingFileFactory(QuickUploadCapableFileFactory):
            def __call__(self, *args, **kwargs):
                raise Exception("nah-ah")

        with TemporaryAdapterRegistration(FailingFileFactory,
                                          required=(IPloneSiteRoot,),
                                          provided=IQuickUploadFileFactory):
            filename = 'qux.txt'
            result = self._upload_file(filename)
            self.assertEqual({u'error': u'serverError'}, result)

    def test_file_factory_error_returns_custom_error(self):
        class ErrorFileFactory(QuickUploadCapableFileFactory):
            def __call__(self, *args, **kwargs):
                return {"error": "It's stone dead", "success": None}

        with TemporaryAdapterRegistration(ErrorFileFactory,
                                          required=(IPloneSiteRoot,),
                                          provided=IQuickUploadFileFactory):
            filename = "qux.txt"
            result = self._upload_file(filename)
            self.assertEqual({u"error": u"It's stone dead"}, result)

    def test_upload_file_twice_unique_id(self):
        filename = 'my-file.jpg'
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        props = portal.portal_properties.quickupload_properties
        props._updateProperty('object_unique_id', True)
        # We must explicitly commit.
        transaction.commit()
        # Upload twice.
        result = self._upload_file(filename)
        result = self._upload_file(filename, 'title two')
        newid = 'my-file-1.jpg'
        self.assertEqual(result.get('success'), True)
        self.assertEqual(result.get('name'), newid)
        self.assertEqual(result.get('title'), 'title two')
        self.assertTrue(newid in portal)
        image2 = portal[newid]
        self.assertEqual(image2.Title(), 'title two')
        self.assertEqual(result.get('uid'), image2.UID())

    def test_upload_file_twice_override(self):
        filename = 'my-file.jpg'
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        props = portal.portal_properties.quickupload_properties
        props._updateProperty('object_override', True)
        # We must explicitly commit, otherwise the change somehow gets lost
        # between the two uploads, presumably due to the explicit commit in
        # uploadcapable.py.
        transaction.commit()
        # Upload twice.
        result = self._upload_file(filename)
        result = self._upload_file(filename, 'title two')
        newid = 'my-file-1.jpg'
        self.assertEqual(result.get('success'), True)
        self.assertEqual(result.get('name'), filename)
        self.assertEqual(result.get('title'), 'title two')
        self.assertFalse(newid in portal)
        image2 = portal[filename]
        self.assertEqual(image2.Title(), 'title two')
        self.assertEqual(result.get('uid'), image2.UID())

    def test_upload_file_twice_default(self):
        filename = 'my-file.jpg'
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        # Upload twice.
        result = self._upload_file(filename)
        result = self._upload_file(filename, 'title two')
        newid = 'my-file-1.jpg'
        self.assertEqual(result.get('error'), 'serverErrorAlreadyExists')
        self.assertFalse(result.get('success'))
        self.assertFalse(newid in portal)
        self.assertTrue(filename in portal)
        image = portal[filename]
        self.assertEqual(image.Title(), 'my file')

    def test_upload_file_id_as_title(self):
        filename = 'my-file.jpg'
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        props = portal.portal_properties.quickupload_properties
        props._updateProperty('id_as_title', True)
        # We must explicitly commit.
        transaction.commit()
        result = self._upload_file(filename)
        self.assertEqual(result.get('success'), True)
        self.assertEqual(result.get('name'), filename)
        self.assertEqual(result.get('title'), filename)
        self.assertTrue(filename in portal)
        image = portal[filename]
        self.assertEqual(image.Title(), filename)

    def test_upload_explicit_title_and_description(self):
        filename = 'my-file.jpg'
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        # With id_as_title True, an explicit title still wins.
        props = portal.portal_properties.quickupload_properties
        props._updateProperty('id_as_title', True)
        # We must explicitly commit.
        transaction.commit()
        title = 'Monty Python'
        description = 'We are the knights who say ni.'
        result = self._upload_file(filename, title, description)
        self.assertEqual(result.get('success'), True)
        self.assertEqual(result.get('name'), filename)
        self.assertEqual(result.get('title'), title)
        self.assertTrue(filename in portal)
        image = portal[filename]
        self.assertEqual(image.Title(), title)
        self.assertEqual(image.Description(), description)
