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
    use_flashupload = Bool(
        title=_(u"title_use_flashupload", default=u"Use Flash Upload"),
        description=_(
            u"description_use_flashupload",
            default=u"By default, the upload script is a javascript only "
                    u"tool. Check this option to replace it with a Flash "
                    u"Upload based script. For modern browsers the javascript "
                    u"tool is more powerful. Flash Upload is just more user "
                    u"friendly under other browsers (MSIE 7, MSIE 8), but has "
                    u"many problems : don't work in https, don't work behind "
                    u"HTTP Authentication ..."),
        default=False,
        required=False)

    use_flash_as_fallback = Bool(
        title=_(u"title_use_flash_fallback",
                default=u"Use flash as fallback for IE"),
        description=_(
            u"description_use_flash_fallback",
            default=u"Check if you want to use flash uload as fallback for IE"
        ),
        default=False,
        required=False)

    auto_upload = Bool(
        title=_(u"title_auto_upload", default=u"Automatic upload on select"),
        description=_(
            u"description_auto_upload",
            default=u"Check if you want to start the files upload on select, "
                    u"without submit the form. Note that you cannot choose "
                    u"file titles or descriptions with this option set to "
                    u"True."),
        default=False,
        required=False)

    show_upload_action = Bool(
        title=_('title_show_upload_action', default=u'Show "Upload" action'),
        description=_(
            'description_show_upload_action', default=u'Check if '
            'you want to have an "Upload" link in your edit bar. Clicking it '
            'will open a panel for uploading below the title of the current '
            'item. This panel is an alternative to the "Upload" portlet and '
            'does not offer any further configuration, such as filtering by '
            'content type. The panel will only be shown where the "Upload" '
            'portlet is not present.'
        ),
        default=False,
        required=False,
    )

    fill_titles = Bool(
        title=_(u"title_fill_titles", default=u"Fill title before upload"),
        description=_(
            u"description_fill_titles",
            default=u"If checked, you can fill the files titles "
                    u"before upload. Uncheck if you don't need titles."),
        default=True,
        required=False)

    fill_descriptions = Bool(
        title=_(
            u"title_fill_descriptions",
            default=u"Fill description before upload"),
        description=_(
            u"description_fill_descriptions",
            default=u"If checked, you can fill the files descriptions "
                    u"before upload. Uncheck if you don't need descriptions."),
        default=False,
        required=False)

    size_limit = Int(
        title=_(u"title_size_limit", default=u"Size limit"),
        description=_(
            u"description_size_limit",
            default=u"Size limit for each file in KB, 0 = no limit"
        ),
        default=0,
        required=True
    )

    sim_upload_limit = Int(
        title=_(
            u"title_sim_upload_limit",
            default=u"Simultaneous uploads limit"
        ),
        description=_(
            u"description_sim_upload_limit",
            default=u"Number of simultaneous files uploaded, over this number "
                    u"uploads are placed in a queue, 0 = no limit"
        ),
        default=2,
        required=True)

    object_unique_id = Bool(
        title=_(u"title_object_unique_id", default=u"Choose unique file id"),
        description=_(
            u"description_object_unique_id",
            default=u"Choose a unique id for each uploaded file."
                    u"Checked: Your files will never be overridden and you'll "
                    u"never get a 'file already exists' error message because "
                    u"each file has its unique id."
                    u"Non-Checked: The id will not be unique. "
                    u"The 'Override by upload file' option is considered "
                    u"when a conflict happens."),
        default=False,
        required=False)

    object_override = Bool(
        title=_(u"title_object_override", default=u"Override by upload file"),
        description=_(
            u"description_object_override",
            default=u"If the folder already has same file name, "
                    u"Checked: Override, Non-Checked: raise upload error."),
        default=True,
        required=False)


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

    def get_use_flash_as_fallback(self):
        return self.quProps.getProperty('use_flash_as_fallback')

    def set_use_flash_as_fallback(self, value):
        self.quProps._updateProperty('use_flash_as_fallback', value)

    use_flash_as_fallback = property(get_use_flash_as_fallback,
                                     set_use_flash_as_fallback)

    def get_auto_upload(self):
        return self.quProps.getProperty('auto_upload')

    def set_auto_upload(self, value):
        self.quProps._updateProperty('auto_upload', value)

    auto_upload = property(get_auto_upload, set_auto_upload)

    def get_show_upload_action(self):
        return self.quProps.getProperty('show_upload_action')

    def set_show_upload_action(self, value):
        self.quProps._updateProperty('show_upload_action', value)

    show_upload_action = property(
        get_show_upload_action, set_show_upload_action)

    def get_fill_titles(self):
        return self.quProps.getProperty('fill_titles')

    def set_fill_titles(self, value):
        self.quProps._updateProperty('fill_titles', value)

    fill_titles = property(get_fill_titles, set_fill_titles)

    def get_fill_descriptions(self):
        return self.quProps.getProperty('fill_descriptions')

    def set_fill_descriptions(self, value):
        self.quProps._updateProperty('fill_descriptions', value)

    fill_descriptions = property(get_fill_descriptions, set_fill_descriptions)

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

    def get_object_unique_id(self):
        return self.quProps.getProperty('object_unique_id')

    def set_object_unique_id(self, value):
        self.quProps._updateProperty('object_unique_id', value)

    object_unique_id = property(get_object_unique_id, set_object_unique_id)

    def get_object_override(self):
        return self.quProps.getProperty('object_override')

    def set_object_override(self, value):
        self.quProps._updateProperty('object_override', value)

    object_override = property(get_object_override, set_object_override)


class QuickUploadControlPanel(ControlPanelForm):

    label = _("Quick Upload settings")
    description = _("""Control how the quick upload tool is used.""")
    form_name = _("Quick Upload settings")
    form_fields = FormFields(IQuickUploadControlPanel)
