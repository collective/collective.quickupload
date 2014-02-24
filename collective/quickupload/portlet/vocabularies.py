# -*- coding: utf-8 -*-
""" Vocabularies used by control panel or widget
"""
from Products.CMFCore.utils import getToolByName
from collective.quickupload import HAS_DEXTERITY
from collective.quickupload import siteMessageFactory as _
from collective.quickupload.browser.quick_upload import _listTypesForInterface
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

if HAS_DEXTERITY:
    from plone.dexterity.interfaces import IDexterityFTI


def _infoDictForType(portal, ptype):
    """
    UI type infos
    @param ptype: a portal type name
    @return: {'portal_type': xxx, 'type_ui_info': UI type info}
    """

    portal_types = getToolByName(portal, 'portal_types')
    type_info = getattr(portal_types, ptype)
    title = type_info.Title()
    if HAS_DEXTERITY and IDexterityFTI.providedBy(type_info):
        product = type_info.klass
    else:
        product = type_info.product
    type_ui_info = ("%s (portal type: %s, product: %s)" %
                    (portal.translate(title, default=title), ptype, product))
    return {
        'portal_type': ptype,
        'type_ui_info': type_ui_info
    }


class UploadFileTypeVocabulary(object):
    """Vocabulary factory for file type upload
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        portal = getToolByName(context, 'portal_url').getPortalObject()
        items = [
            SimpleTerm(
                'auto', 'auto', context.translate(_(
                    'label_default_portaltype_configuration',
                    default=u'Default configuration (Content Type Registry).'))
            )
        ]

        flt = [
            _infoDictForType(portal, tipe) for tipe in
            _listTypesForInterface(portal, 'file')
        ]
        ilt = [
            _infoDictForType(portal, tipe) for tipe in
            _listTypesForInterface(portal, 'image')
        ]
        items.extend([
            SimpleTerm(
                t['portal_type'], t['portal_type'], t['type_ui_info']
            )
            for t in flt
        ])
        file_types = [t['portal_type'] for t in flt]
        items.extend([
            SimpleTerm(
                t['portal_type'], t['portal_type'], t['type_ui_info']
            )
            for t in ilt if t['portal_type'] not in file_types
        ])

        return SimpleVocabulary(items)


UploadFileTypeVocabularyFactory = UploadFileTypeVocabulary()
