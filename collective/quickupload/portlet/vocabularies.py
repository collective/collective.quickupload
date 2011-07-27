# -*- coding: utf-8 -*-

""" Vocabularies used by control panel or widget
"""

from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from Products.ATContentTypes.interfaces import IFileContent, IImageContent
from Products.CMFCore.utils import getToolByName

from collective.quickupload.browser.quick_upload import _listTypesForInterface

def _infoDictForType(portal, ptype ):
    """
    UI type infos
    @param ptype: a portal type name
    @return: {'portal_type': xxx, 'type_ui_info': UI type info}
    """

    portal_types = getToolByName(portal, 'portal_types')
    type_info = getattr(portal_types, ptype)
    title = type_info.Title()
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
        flt = [_infoDictForType(portal, tipe) for tipe in _listTypesForInterface(portal, IFileContent)]
        ilt = [_infoDictForType(portal, tipe) for tipe in _listTypesForInterface(portal, IImageContent)]
        items = [SimpleTerm('auto', 'auto', context.translate('label_default_portaltype_configuration',
                                                      default=u'Default configuration (Content Type Registry).',
                                                      domain='collective.quickupload')),]
        items.extend([ SimpleTerm(t['portal_type'], t['portal_type'], t['type_ui_info'])
                  for t in flt ])
        items.extend([ SimpleTerm(t['portal_type'], t['portal_type'], t['type_ui_info'])
                  for t in ilt ])
        return SimpleVocabulary(items)


UploadFileTypeVocabularyFactory = UploadFileTypeVocabulary()

