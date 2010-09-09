from zope.interface import Interface, implements
from zope.component import adapts
from zope.schema import Bool, Int
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName
from zope.formlib.form import FormFields
from plone.app.controlpanel.form import ControlPanelForm
from collective.quickupload import siteMessageFactory as _


class IQuickUploadControlPanel(Interface):
    """
    fields for quick upload control panel
    """
    use_flashupload = Bool(title=_(u"Use Flashupload"),
                           description=_(u"By default, the upload script is a javascript only tool. "
                                          "You can choose to replace it with a Flash upload based script. "
                                          "Take care : Flash Upload don't work behind an HTTP Authenticated server "
                                          "(Apache + Basic authentication, IIS + Windows NT Authentication ...) "),
                           default=False,
                           required=False)    
    auto_upload = Bool(title=_(u"Automatic upload on select"),
                                 description=_(u"Check if you want to start the files upload on select, without submit. "
                                                "Note that you cannot choose file titles "
                                                "with this option set to True. "),
                                 default=False,
                                 required=False) 
    fill_titles = Bool(title=_(u"Fill title before upload"),
                                 description=_(u"If checked, you can fill the files titles "
                                                "before upload. Uncheck if you don't need titles."),
                                 default=True,
                                 required=False) 

    size_limit = Int( title=_(u"Size limit"),
                      description=_(u"Size limit for each file in KB, 0 = no limit"),
                      default=0,
                      required=True)

    sim_upload_limit = Int( title=_(u"Silmutaneous uploads limit"),
                            description=_(u"Number of silmutaneous files uploaded, over this number uploads are placed in a queue, 0 = no limit"),
                            default=2,
                            required=True)

class QuickUploadControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IQuickUploadControlPanel)

    def __init__(self, context):
        super(QuickUploadControlPanelAdapter, self).__init__(context)
        pprop = getToolByName(context, 'portal_properties')
        self.quProps = pprop.quickupload_properties

    def get_use_flashupload(self):
        return self.quProps.getProperty('use_flashupload')
        
    def set_use_flashupload(self, value):
        self.quProps._updateProperty('use_flashupload', value)

    use_flashupload = property(get_use_flashupload, set_use_flashupload)

    def get_auto_upload(self):
        return self.quProps.getProperty('auto_upload')
        
    def set_auto_upload(self, value):
        self.quProps._updateProperty('auto_upload', value)

    auto_upload = property(get_auto_upload, set_auto_upload)

    def get_fill_titles(self):
        return self.quProps.getProperty('fill_titles')
        
    def set_fill_titles(self, value):
        self.quProps._updateProperty('fill_titles', value)

    fill_titles = property(get_fill_titles, set_fill_titles)

    def get_size_limit(self):
        return self.quProps.getProperty('size_limit')
        
    def set_size_limit(self, value):
        self.quProps._updateProperty('size_limit', value)

    size_limit = property(get_size_limit, set_size_limit)

    def get_sim_upload_limit(self):
        return self.quProps.getProperty('sim_upload_limit')
        
    def set_sim_upload_limit(self, value):
        self.quProps._updateProperty('sim_upload_limit', value)

    sim_upload_limit = property(get_sim_upload_limit, set_sim_upload_limit)


class QuickUploadControlPanel(ControlPanelForm):

    label = _("Quick Upload settings")
    description = _("""Control how the quick upload tool is used.""")
    form_name = _("Quick Upload settings")
    form_fields = FormFields(IQuickUploadControlPanel)