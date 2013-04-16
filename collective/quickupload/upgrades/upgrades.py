from Products.CMFCore.utils import getToolByName


def v1_v2(context):
    upgrade_resources(context)


def v2_v3(context):
    upgrade_resources(context)


def upgrade_resources(context):
    context.runImportStepFromProfile('profile-collective.quickupload:default',
                                     'jsregistry')
    context.runImportStepFromProfile('profile-collective.quickupload:default',
                                     'cssregistry')
    getToolByName(context, 'portal_css').cookResources()
    getToolByName(context, 'portal_javascripts').cookResources()


def v3_v4(context):
    #Add property to quickupload property sheet
    ptool = getToolByName(context, 'portal_properties')
    qu_props = ptool.get('quickupload_properties')
    qu_props._setProperty('use_flash_as_fallback', False, 'boolean')


def v4_v5(context):
    #Add property to quickupload property sheet
    ptool = getToolByName(context, 'portal_properties')
    qu_props = ptool.get('quickupload_properties')
    if not qu_props.hasProperty('show_upload_action'):
        qu_props._setProperty('show_upload_action', False, 'boolean')
    context.runImportStepFromProfile(
        'profile-collective.quickupload:default', 'actions')
