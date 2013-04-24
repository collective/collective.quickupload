# -*- coding: utf-8 -*-
import unittest2 as unittest

from zope.interface import Interface
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.content import Item
from plone.dexterity.fti import DexterityFTI, register
from plone.namedfile import field
from plone.namedfile.interfaces import INamedFile, INamedImage
try:
    from plone.namedfile.interfaces import INamedBlobFile, INamedBlobImage
    HAVE_BLOBS = True
except:
    HAVE_BLOBS = False

from collective.quickupload.testing import QUICKUPLOAD_INTEGRATION_TESTING
from collective.quickupload.interfaces import IQuickUploadFileSetter
from collective.quickupload.dexterity import DexterityFileSetter


FILENAME_TESTSTRING = u"Iñtërnâtiônàlizætiøn Ξεσκεπάζω tükörfúrógép äß \
いろはにほへとちりぬるを イロハニホヘト הקליטה łódź чащах มนุษย์ yağız şoföre \
::_-^°*#',;<>{}[]¡“¶¢|¿≠å+.§$%&()=?€¥±–…∞µ~∫√≈ƒ©ªº@•π⁄Ω†®∑«»\""


class ISchemaWithNamedFile(Interface):
    field = field.NamedFile()


class ISchemaWithNamedImage(Interface):
    field = field.NamedImage()


if HAVE_BLOBS:
    class ISchemaWithNamedBlobFile(Interface):
        field = field.NamedBlobFile()

    class ISchemaWithNamedBlobImage(Interface):
        field = field.NamedBlobImage()


class TestCase(unittest.TestCase):

    layer = QUICKUPLOAD_INTEGRATION_TESTING

    @property
    def portal(self):
        return self.layer['portal']

    def getFileSetter(self, schema):
        portal_type = 'testtype'
        setRoles(self.portal, TEST_USER_ID, ('Manager',))

        # prepare a fti
        fti = DexterityFTI(portal_type)
        fti.klass = 'plone.dexterity.content.Item'
        fti.schema = schema.__identifier__
        self.portal.portal_types._setObject(portal_type, fti)
        register(fti)

        # prepare an item
        item = Item('testitem')
        item.portal_type = portal_type
        self.portal._setObject(item.id, item)
        item = self.portal[item.id]

        return IQuickUploadFileSetter(item)

    def test_adapting(self):
        item = Item()
        fileSetter = IQuickUploadFileSetter(item)
        self.failUnless(fileSetter.__class__ is DexterityFileSetter)

    def test_namedfile_setting(self):
        data = 'datattatatata'
        filename = FILENAME_TESTSTRING + u".xlsx"
        content_type = 'application/vnd.ms-excel'

        fileSetter = self.getFileSetter(ISchemaWithNamedFile)
        fileSetter.set(data, filename.encode('utf-8'), content_type)
        field = fileSetter.context.field

        self.assertTrue(INamedFile.providedBy(field))
        self.assertEqual(field.filename, filename)
        self.assertEqual(field.contentType, content_type)
        self.assertEqual(field.data, data)

    def test_namedimage_setting(self):
        data = 'datattatatata'
        filename = FILENAME_TESTSTRING + u".jpeg"
        content_type = 'image/jpeg'

        fileSetter = self.getFileSetter(ISchemaWithNamedImage)
        fileSetter.set(data, filename.encode('utf-8'), content_type)
        field = fileSetter.context.field

        self.assertTrue(INamedImage.providedBy(field))
        self.assertEqual(field.filename, filename)
        self.assertEqual(field.contentType, content_type)
        self.assertEqual(field.data, data)

    if HAVE_BLOBS:
        def test_namedblobfile_setting(self):
            data = 'datattatatata'
            filename = FILENAME_TESTSTRING + u".xlsx"
            content_type = 'application/vnd.ms-excel'

            fileSetter = self.getFileSetter(ISchemaWithNamedBlobFile)
            fileSetter.set(data, filename.encode('utf-8'), content_type)
            field = fileSetter.context.field

            self.assertTrue(INamedBlobFile.providedBy(field))
            self.assertEqual(field.filename, filename)
            self.assertEqual(field.contentType, content_type)
            self.assertEqual(field.data, data)

        def test_namedblobimage_setting(self):
            data = 'datattatatata'
            filename = FILENAME_TESTSTRING + u".jpeg"
            content_type = 'image/jpeg'

            fileSetter = self.getFileSetter(ISchemaWithNamedBlobImage)
            fileSetter.set(data, filename.encode('utf-8'), content_type)
            field = fileSetter.context.field

            self.assertTrue(INamedBlobImage.providedBy(field))
            self.assertEqual(field.filename, filename)
            self.assertEqual(field.contentType, content_type)
            self.assertEqual(field.data, data)
