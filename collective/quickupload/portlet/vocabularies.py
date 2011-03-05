# -*- coding: utf-8 -*-  

""" Vocabularies used by control panel or widget
"""

from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
try:
    # Zope 2.13
    from zope.component.hooks import getSite
except ImportError:
    # Zope 2.12
    from zope.site.hooks import getSite
from Products.ATContentTypes.interfaces import IFileContent, IImageContent
from Products.CMFCore.utils import getToolByName

def _listTypesForInterface(portal, interface):
    """
    List of portal types that have File interface
    @param portal: plone site
    @param interface: Zope 2 inteface
    @return: [{'portal_type': xx, 'type_ui_info': UI type info}, ...]
    """
 
    archetype_tool = getToolByName(portal, 'archetype_tool')
    
    #plone4
    try :
        all_types = [tipe.getId() for tipe in archetype_tool.listPortalTypesWithInterfaces([interface])]
    #plone3
    except :
        all_types = archetype_tool.listRegisteredTypes(inProject=True)
        all_types = [tipe['portal_type'] for tipe in all_types
                     if interface.isImplementedByInstancesOf(tipe['klass'])]
    
    # fix for bug in listRegisteredTypes which returns 2 'ATFolder'
    # when asking for IBaseFolder interface
    unik_types = dict.fromkeys(all_types).keys() 
    return [_infoDictForType(portal, tipe) for tipe in unik_types]
    
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
        portal = getSite()
        flt = _listTypesForInterface(portal, IFileContent)
        ilt = _listTypesForInterface(portal, IImageContent)
        items = [SimpleTerm('auto', 'auto', context.translate('label_default_portaltype_configuration', 
                                                      default=u'Default configuration (Content Type Registry).', 
                                                      domain='collective.quickupload')),]
        items.extend([ SimpleTerm(t['portal_type'], t['portal_type'], t['type_ui_info'])
                  for t in flt ])
        items.extend([ SimpleTerm(t['portal_type'], t['portal_type'], t['type_ui_info'])
                  for t in ilt ])
        return SimpleVocabulary(items)        
        

UploadFileTypeVocabularyFactory = UploadFileTypeVocabulary()

