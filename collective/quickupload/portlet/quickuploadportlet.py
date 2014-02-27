# -*- coding: utf-8 -*-
## Copyright (C)2010 Alter Way Solutions
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.FactoryTool import TempFolder
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Sessions.SessionDataManager import SessionDataManagerErr
from collective.quickupload import logger
from collective.quickupload import siteMessageFactory as _
from collective.quickupload.interfaces import IQuickUploadCapable
from collective.quickupload.interfaces import IQuickUploadNotCapable
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from plone.app.portlets.portlets import base
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.formlib import form
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
PMF = MessageFactory('plone')


def isTemporary(obj):
    """Check to see if an object is temporary"""
    if not shasattr(obj, 'isTemporary'):
        return False
    if obj.isTemporary():
        return False

    parent = aq_base(aq_parent(aq_inner(obj)))
    return hasattr(parent, 'meta_type') \
        and parent.meta_type == TempFolder.meta_type


JAVASCRIPT = """
  // workaround this MSIE bug :
  // https://dev.plone.org/plone/ticket/10894
  if (jQuery.browser.msie) jQuery("#settings").remove();
  var Browser = {};
  Browser.onUploadComplete = function() {
      window.location.reload();
  }
  loadUploader = function() {
      var ulContainer = jQuery('.QuickUploadPortlet .uploaderContainer');
      ulContainer.each(function(){
          var uploadUrl =  jQuery('.uploadUrl', this).val();
          var uploadData =  jQuery('.uploadData', this).val();
          var UlDiv = jQuery(this);
          jQuery.ajax({
                     type: 'GET',
                     url: uploadUrl,
                     data: uploadData,
                     dataType: 'html',
                     contentType: 'text/html; charset=utf-8',
                     success: function(html) {
                        if (html.indexOf('quick-uploader') != -1) {
                            UlDiv.html(html);
                        }
                     } });
      });
  }
  jQuery(document).ready(loadUploader);
"""


class IQuickUploadPortlet(IPortletDataProvider):
    """Quickupload portlet schema
    """

    header = schema.TextLine(
        title=_(u"Box title"),
        default=u"",
        description=_(u"If title is empty, the portlet title will be the "
                      u"Media Choice + ' Quick Upload'."),
        required=False)

    upload_portal_type = schema.Choice(
        title=_(u"Content type"),
        description=_(u"Choose the portal type used for file upload. "
                      u"Let the default configuration for an automatic portal "
                      u"type, depending on settings defined in "
                      u"content_type_registry."),
        required=True,
        default='auto',
        vocabulary="collective.quickupload.fileTypeVocabulary")

    upload_media_type = schema.Choice(
        title=_(u"Media type"),
        description=_(u"Choose the media type used for file upload. "
                      u"image, audio, video ..."),
        required=False,
        default='',
        vocabulary=SimpleVocabulary(
            [SimpleTerm('', '', _(u"All")),
             SimpleTerm('image', 'image', _(u"Images")),
             SimpleTerm('video', 'video', _(u"Video files")),
             SimpleTerm('audio', 'audio', _(u"Audio files")),
             SimpleTerm('flash', 'flash', _(u"Flash files"))]
        ),
    )


class Assignment(base.Assignment):
    """Portlet assignment.
    """

    implements(IQuickUploadPortlet)

    def __init__(self, header='', upload_portal_type='auto',
                 upload_media_type=''):
        self.header = header
        self.upload_portal_type = upload_portal_type
        self.upload_media_type = upload_media_type

    @property
    def title(self):
        """portlet title
        """
        if self.header:
            return PMF(self.header)

        media = self.upload_media_type
        if not media or '*.' in media:
            return _(u'Files Quick Upload')
        elif media == 'image':
            return _(u'Images Quick Upload')
        else:
            return _(u'label_media_quickupload',
                     default='${medialabel} Quick Upload',
                     mapping={'medialabel': media.capitalize()})


class Renderer(base.Renderer):
    """Portlet renderer.
    """

    _template = ViewPageTemplateFile('quickuploadportlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        context = aq_inner(self.context)
        self.ploneview = context.restrictedTraverse('@@plone')
        self.pm = getToolByName(context, 'portal_membership')

    def _clean_session(self):
        request = self.request
        try:
            session = request.get('SESSION', None)
        except SessionDataManagerErr:
            logger.debug(
                'Error occurred getting session data. Falling back to request.'
            )
            session = None
        # empty typeupload and mediaupload session
        # since the portlet don't use it, but another app could
        if session:
            # session does not implement dict API. it's a TransientObject
            if session.has_key('typeupload'):
                session.delete('typeupload')
            if session.has_key('mediaupload'):
                session.delete('mediaupload')

    def render(self):
        self._clean_session()
        return xhtml_compress(self._template())

    @property
    def available(self):
        if not (IViewView.providedBy(self.view)
                or IFolderContentsView.providedBy(self.view)):
            return False

        context = aq_inner(self.context)

        if not IQuickUploadCapable.providedBy(context):
            return False
        elif IQuickUploadNotCapable.providedBy(context):
            return False
        elif not self.pm.checkPermission('Add portal content', context):
            return False
        elif isTemporary(context):
            return False

        upload_portal_type = self.data.upload_portal_type
        if (upload_portal_type and upload_portal_type != 'auto'
                and upload_portal_type not in [
                    t.id for t in self.context.getAllowedTypes()
                ]):
            return False
        else:
            return True

    def getUploadUrl(self):
        """
        return upload url
        in current folder
        """
        folder_url = self.ploneview.getCurrentFolderUrl()
        return '%s/@@quick_upload' % folder_url

    def getDataForUploadUrl(self):
        data_url = ''
        if self.data.upload_portal_type != 'auto':
            data_url += 'typeupload=%s&' % self.data.upload_portal_type
        if self.data.upload_media_type:
            data_url += 'mediaupload=%s' % self.data.upload_media_type
        return data_url

    def javascript(self):
        return JAVASCRIPT


class AddForm(base.AddForm):
    """Portlet add form.
    """
    form_fields = form.Fields(IQuickUploadPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.
    """
    form_fields = form.Fields(IQuickUploadPortlet)
