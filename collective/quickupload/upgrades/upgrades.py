
def v1_v2(context):
    context.runImportStepFromProfile('profile-collective.quickupload:default',
                                     'jsregistry')
    context.runImportStepFromProfile('profile-collective.quickupload:default',
                                     'cssregistry')