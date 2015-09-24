# code taken from collective.uploadify
# for the flashupload
# with many ameliorations
from AccessControl import SecurityManagement
from Acquisition import aq_inner, aq_parent
from Products.ATContentTypes.interfaces import IFileContent
from Products.ATContentTypes.interfaces import IImageContent
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Sessions.SessionDataManager import SessionDataManagerErr
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPRequest import FileUpload
from collective.quickupload import HAS_DEXTERITY
from collective.quickupload import logger
from collective.quickupload import siteMessageFactory as _
from collective.quickupload.browser.quickupload_settings import IQuickUploadControlPanel
from collective.quickupload.browser.uploadcapable import MissingExtension
from collective.quickupload.browser.uploadcapable import get_id_from_filename
from collective.quickupload.browser.utils import can_dnd
from collective.quickupload.interfaces import IQuickUploadFileFactory
from collective.quickupload.interfaces import IQuickUploadFileUpdater
from collective.quickupload.interfaces import IQuickUploadNotCapable
from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer
from ZODB.POSException import ConflictError
from zope.component import getUtility
from zope.i18n import translate
from zope.schema import getFieldsInOrder
from zope.security.interfaces import Unauthorized

import mimetypes
import os
import random
import ticket as ticketmod
import urllib


import pkg_resources
try:
    pkg_resources.get_distribution('plone.uuid')
    from plone.uuid.interfaces import IUUID
    HAS_UUID = True
except pkg_resources.DistributionNotFound:
    HAS_UUID = False

if HAS_DEXTERITY:
    from plone.dexterity.interfaces import IDexterityFTI
    from plone.namedfile.interfaces import INamedFileField
    from plone.namedfile.interfaces import INamedImageField

try:
    # Python 2.6+
    import json
except ImportError:
    # Python 2.4 (Plone 3.3)
    import simplejson as json


def decodeQueryString(QueryString):
    """decode *QueryString* into a dictionary, as ZPublisher would do"""
    r = HTTPRequest(
        None,
        {'QUERY_STRING': QueryString, 'SERVER_URL': '', },
        None,
        1
    )
    r.processInputs()
    return r.form


def getDataFromAllRequests(request, dataitem):
    """Sometimes data is send using POST METHOD and QUERYSTRING
    """
    data = request.form.get(dataitem, None)
    if data is None:
        # try to get data from QueryString
        data = decodeQueryString(request.get('QUERY_STRING', '')).get(dataitem)
    return data


def find_user(context, userid):
    """Walk up all of the possible acl_users to find the user with the
    given userid.
    """

    track = set()

    acl_users = aq_inner(getToolByName(context, 'acl_users'))
    path = '/'.join(acl_users.getPhysicalPath())
    logger.debug('Visited acl_users "%s"' % path)
    track.add(path)

    user = acl_users.getUserById(userid)
    while user is None and acl_users is not None:
        context = aq_parent(aq_parent(aq_inner(acl_users)))
        acl_users = aq_inner(getToolByName(context, 'acl_users'))
        if acl_users is not None:
            path = '/'.join(acl_users.getPhysicalPath())
            logger.debug('Visited acl_users "%s"' % path)
            if path in track:
                logger.warn('Tried searching an already visited acl_users, '
                            '"%s".  All visited are: %r' % (path, list(track)))
                break
            track.add(path)
            user = acl_users.getUserById(userid)

    if user is not None:
        user = user.__of__(acl_users)

    return user


def _listTypesForInterface(context, iftype='file'):
    """
    List of portal types that have File or Image interface
    @param portal: context
    @param iftype:
        Type of interface to query for, can be either 'file' or 'image'
    @return: ['Image', 'News Item']
    """

    archetype_tool = getToolByName(context, 'archetype_tool', None)
    types_tool = getToolByName(context, 'portal_types')

    all_types = []
    if archetype_tool:
        if iftype == 'image':
            interface = IImageContent
        else:
            interface = IFileContent
        #plone4
        try:
            all_types = [
                tipe.getId() for tipe in
                archetype_tool.listPortalTypesWithInterfaces([interface])
            ]
        #plone3
        except:
            all_types = archetype_tool.listRegisteredTypes(inProject=True)
            all_types = [
                tipe['portal_type'] for tipe in all_types
                if interface.isImplementedByInstancesOf(tipe['klass'])
            ]

    if HAS_DEXTERITY:
        if iftype == 'image':
            interface = INamedImageField
        else:
            interface = INamedFileField
        for fti in types_tool.objectValues():
            if IDexterityFTI.providedBy(fti):
                fields = getFieldsInOrder(fti.lookupSchema())
                for fieldname, field in fields:
                    if interface.providedBy(field):
                        all_types.append(fti.getId())
                        break

    # fix for bug in listRegisteredTypes which returns 2 'ATFolder'
    # when asking for IBaseFolder interface
    unik_types = dict.fromkeys(all_types).keys()
    return unik_types


class QuickUploadView(BrowserView):
    """ The Quick Upload View
    """

    template = ViewPageTemplateFile("quick_upload.pt")

    def __init__(self, context, request):
        super(QuickUploadView, self).__init__(context, request)
        self.uploader_id = self._uploader_id()

    def __call__(self):
        if IQuickUploadNotCapable.providedBy(self.context):
            raise Unauthorized

        # disable diazo themes
        self.request.response.setHeader('X-Theme-Disabled', 'True')

        return self.template()

    def header_upload(self):
        request = self.request
        try:
            session = request.get('SESSION', {})
            medialabel = session.get(
                'mediaupload',
                request.get('mediaupload', 'files')
            )
        except SessionDataManagerErr:
            logger.debug('Error occurred getting session data. '
                         'Falling back to request.')
            medialabel = request.get('mediaupload', 'files')

        # to improve
        if '*.' in medialabel:
            medialabel = ''
        if not medialabel:
            return _('Files Quick Upload')
        elif medialabel == 'image':
            return _('Images Quick Upload')
        else:
            return _('label_media_quickupload',
                     default='${medialabel} Quick Upload',
                     mapping={'medialabel': translate(
                         medialabel.capitalize(),
                         domain='collective.quickupload',
                         context=self.request)
                     })

    def _uploader_id(self):
        return 'uploader%s' % str(random.random()).replace('.', '')

    def script_content(self):
        context = aq_inner(self.context)
        return context.restrictedTraverse('@@quick_upload_init')(
            for_id=self.uploader_id
        )

    def can_drag_and_drop(self):
        user_agent = self.request.get_header('User-Agent')
        return can_dnd(user_agent)


XHR_UPLOAD_JS = """
    var fillTitles = %(ul_fill_titles)s;
    var fillDescriptions = %(ul_fill_descriptions)s;
    var auto = %(ul_auto_upload)s;
    addUploadFields_%(ul_id)s = function(file, id) {
        var uploader = xhr_%(ul_id)s;
        PloneQuickUpload.addUploadFields(uploader, uploader._element, file, id, fillTitles, fillDescriptions);
    }
    sendDataAndUpload_%(ul_id)s = function() {
        var uploader = xhr_%(ul_id)s;
        PloneQuickUpload.sendDataAndUpload(uploader, uploader._element, '%(typeupload)s');
    }
    clearQueue_%(ul_id)s = function() {
        var uploader = xhr_%(ul_id)s;
        PloneQuickUpload.clearQueue(uploader, uploader._element);
    }
    onUploadComplete_%(ul_id)s = function(id, fileName, responseJSON) {
        var uploader = xhr_%(ul_id)s;
        PloneQuickUpload.onUploadComplete(uploader, uploader._element, id, fileName, responseJSON);
    }
    createUploader_%(ul_id)s= function(){
        xhr_%(ul_id)s = new qq.FileUploader({
            element: jQuery('#%(ul_id)s')[0],
            action: '%(context_url)s/@@quick_upload_file',
            autoUpload: auto,
            onAfterSelect: addUploadFields_%(ul_id)s,
            onComplete: onUploadComplete_%(ul_id)s,
            allowedExtensions: %(ul_file_extensions_list)s,
            sizeLimit: %(ul_xhr_size_limit)s,
            simUploadLimit: %(ul_sim_upload_limit)s,
            template: '<div class="qq-uploader">' +
                      '<div class="qq-upload-drop-area"><span>%(ul_draganddrop_text)s</span></div>' +
                      '<div class="qq-upload-button">%(ul_button_text)s</div>' +
                      '<ul class="qq-upload-list"></ul>' +
                      '</div>',
            fileTemplate: '<li>' +
                    '<a class="qq-upload-cancel" href="#">&nbsp;</a>' +
                    '<div class="qq-upload-infos"><span class="qq-upload-file"></span>' +
                    '<span class="qq-upload-spinner"></span>' +
                    '<span class="qq-upload-failed-text">%(ul_msg_failed)s</span></div>' +
                    '<div class="qq-upload-size"></div>' +
                '</li>',
            messages: {
                serverError: "%(ul_error_server)s",
                serverErrorAlreadyExists: "%(ul_error_already_exists)s {file}",
                serverErrorZODBConflict: "%(ul_error_zodb_conflict)s {file}, %(ul_error_try_again)s",
                serverErrorNoPermission: "%(ul_error_no_permission)s",
                serverErrorDisallowedType: "%(ul_error_disallowed_type)s",
                typeError: "%(ul_error_bad_ext)s {file}. %(ul_error_onlyallowed)s {extensions}.",
                sizeError: "%(ul_error_file_large)s {file}, %(ul_error_maxsize_is)s {sizeLimit}.",
                emptyError: "%(ul_error_empty_file)s {file}, %(ul_error_try_again_wo)s",
                missingExtension: "%(ul_error_empty_extension)s {file}"
            }
        });
    }
    jQuery(document).ready(createUploader_%(ul_id)s);
"""

FLASH_UPLOAD_JS = """
    var fillTitles = %(ul_fill_titles)s;
    var fillDescriptions = %(ul_fill_descriptions)s;
    var autoUpload = %(ul_auto_upload)s;
    clearQueue_%(ul_id)s = function() {
        jQuery('#%(ul_id)s').uploadifyClearQueue();
    }
    addUploadifyFields_%(ul_id)s = function(event, data ) {
        if ((fillTitles || fillDescriptions) && !autoUpload)  {
            var labelfiletitle = jQuery('#uploadify_label_file_title').val();
            var labelfiledescription = jQuery('#uploadify_label_file_description').val();
            jQuery('#%(ul_id)sQueue .uploadifyQueueItem').each(function() {
                ID = jQuery(this).attr('id').replace('%(ul_id)s','');
                if (!jQuery('.uploadField' ,this).length) {
                  jQuery('.cancel' ,this).after('\
                          <input type="hidden" \
                                 class="file_id_field" \
                                 name="file_id" \
                                 value ="'  + ID + '" /> \
                  ');
                  if (fillDescriptions) jQuery('.cancel' ,this).after('\
                      <div class="uploadField">\
                          <label>' + labelfiledescription + ' : </label> \
                          <textarea rows="2" \
                                 class="file_description_field" \
                                 id="description_' + ID + '" \
                                 name="description" \
                                 value="" />\
                      </div>\
                  ');
                  if (fillTitles) jQuery('.cancel' ,this).after('\
                      <div class="uploadField">\
                          <label>' + labelfiletitle + ' : </label> \
                          <input type="text" \
                                 class="file_title_field" \
                                 id="title_' + ID + '" \
                                 name="title" \
                                 value="" />\
                      </div>\
                  ');
                }
            });
        }
        if (!autoUpload) return showButtons_%(ul_id)s();
        return 'ok';
    }
    showButtons_%(ul_id)s = function() {
        if (jQuery('#%(ul_id)sQueue .uploadifyQueueItem').length) {
            jQuery('.uploadifybuttons').show();
            return 'ok';
        }
        return false;
    }
    sendDataAndUpload_%(ul_id)s = function() {
        QueueItems = jQuery('#%(ul_id)sQueue .uploadifyQueueItem');
        nbItems = QueueItems.length;
        QueueItems.each(function(i){
            filesData = {};
            ID = jQuery('.file_id_field',this).val();
            if (fillTitles && !autoUpload) {
                filesData['title'] = jQuery('.file_title_field',this).val();
            }
            if (fillDescriptions && !autoUpload) {
                filesData['description'] = jQuery('.file_description_field',this).val();
            }
            jQuery('#%(ul_id)s').uploadifySettings('scriptData', filesData);
            jQuery('#%(ul_id)s').uploadifyUpload(ID);
        })
    }
    onAllUploadsComplete_%(ul_id)s = function(event, data){
        if (!data.errors) {
           Browser.onUploadComplete();
        }
        else {
           msg= data.filesUploaded + '%(ul_msg_some_sucess)s' + data.errors + '%(ul_msg_some_errors)s';
           alert(msg);
        }
    }
    jQuery(document).ready(function() {
        jQuery('#%(ul_id)s').uploadify({
            'uploader'      : '%(portal_url)s/++resource++quickupload_static/uploader.swf',
            'script'        : '%(context_url)s/@@flash_upload_file',
            'cancelImg'     : '%(portal_url)s/++resource++quickupload_static/cancel.png',
            'folder'        : '%(physical_path)s',
            'onAllComplete' : onAllUploadsComplete_%(ul_id)s,
            'auto'          : autoUpload,
            'multi'         : true,
            'simUploadLimit': %(ul_sim_upload_limit)s,
            'sizeLimit'     : '%(ul_size_limit)s',
            'fileDesc'      : '%(ul_file_description)s',
            'fileExt'       : '%(ul_file_extensions)s',
            'buttonText'    : '%(ul_button_text)s',
            'scriptAccess'  : 'sameDomain',
            'hideButton'    : false,
            'onSelectOnce'  : addUploadifyFields_%(ul_id)s,
            'scriptData'    : {'ticket' : '%(ticket)s', 'typeupload' : '%(typeupload)s'}
        });
    });
"""


class QuickUploadInit(BrowserView):
    """ Initialize uploadify js
    """

    def __init__(self, context, request):
        super(QuickUploadInit, self).__init__(context, request)
        self.context = aq_inner(context)
        portal = getUtility(IPloneSiteRoot)
        self.qup_prefs = IQuickUploadControlPanel(portal)

    def ul_content_types_infos(self, mediaupload):
        """
        return some content types infos depending on mediaupload type
        mediaupload could be 'image', 'video', 'audio' or any
        extension like '*.doc'
        """
        ext = '*.*;'
        extlist = []
        msg = u'Choose files to upload'
        if mediaupload == 'image':
            ext = '*.jpg;*.jpeg;*.gif;*.png;'
            msg = _(u'Choose images to upload')
        elif mediaupload == 'video':
            ext = '*.flv;*.avi;*.wmv;*.mpg;'
            msg = _(u'Choose video files to upload')
        elif mediaupload == 'audio':
            ext = '*.mp3;*.wav;*.ogg;*.mp4;*.wma;*.aif;'
            msg = _(u'Choose audio files to upload')
        elif mediaupload == 'flash':
            ext = '*.swf;'
            msg = _(u'Choose flash files to upload')
        elif mediaupload:
            # you can also pass a list of extensions in mediaupload request var
            # with this syntax '*.aaa;*.bbb;'
            ext = mediaupload
            msg = _(u'Choose file for upload: ${ext}', mapping={'ext': ext})

        try:
            extlist = [
                f.split('.')[1].strip() for f in ext.split(';') if f.strip()
            ]
        except:
            extlist = []
        if extlist == ['*']:
            extlist = []

        return (ext, extlist, self._translate(msg))

    def _translate(self, msg):
        return translate(msg, context=self.request)

    def upload_settings(self):
        context = aq_inner(self.context)
        request = self.request
        try:
            session = request.get('SESSION', {})
            mediaupload = session.get(
                'mediaupload', request.get('mediaupload', ''))
            typeupload = session.get(
                'typeupload', request.get('typeupload', ''))
        except SessionDataManagerErr:
            logger.debug(
                'Error occurred getting session data. Falling back to request.'
            )
            mediaupload = request.get('mediaupload', '')
            typeupload = request.get('typeupload', '')
        portal_url = getToolByName(context, 'portal_url')()
        # use a ticket for authentication (used for flashupload only)
        ticket = context.restrictedTraverse('@@quickupload_ticket')()

        settings = dict(
            ticket                 = ticket,
            portal_url             = portal_url,
            typeupload             = '',
            context_url            = context.absolute_url(),
            physical_path          = "/".join(context.getPhysicalPath()),
            ul_id                  = self.uploader_id,
            ul_fill_titles         = self.qup_prefs.fill_titles and 'true' or 'false',
            ul_fill_descriptions   = self.qup_prefs.fill_descriptions and 'true' or 'false',
            ul_auto_upload         = self.qup_prefs.auto_upload and 'true' or 'false',
            ul_size_limit          = self.qup_prefs.size_limit and str(self.qup_prefs.size_limit*1024) or '',
            ul_xhr_size_limit      = self.qup_prefs.size_limit and str(self.qup_prefs.size_limit*1024) or '0',
            ul_sim_upload_limit    = str(self.qup_prefs.sim_upload_limit),
            ul_object_override     = self.qup_prefs.object_override and 'true' or 'false',
            ul_button_text         = self._translate(_(u'Browse')),
            ul_draganddrop_text    = self._translate(_(u'Drag and drop files to upload')),
            ul_msg_all_sucess      = self._translate(_(u'All files uploaded with success.')),
            ul_msg_some_sucess     = self._translate(_(u' files uploaded with success, ')),
            ul_msg_some_errors     = self._translate(_(u" uploads return an error.")),
            ul_msg_failed          = self._translate(_(u"Failed")),
            ul_error_try_again_wo  = self._translate(_(u"please select files again without it.")),
            ul_error_try_again     = self._translate(_(u"please try again.")),
            ul_error_empty_file    = self._translate(_(u"Selected elements contain an empty file or a folder:")),
            ul_error_empty_extension = self._translate(_(u"This file has no extension:")),
            ul_error_file_large    = self._translate(_(u"This file is too large:")),
            ul_error_maxsize_is    = self._translate(_(u"maximum file size is:")),
            ul_error_bad_ext       = self._translate(_(u"This file has invalid extension:")),
            ul_error_onlyallowed   = self._translate(_(u"Only allowed:")),
            ul_error_no_permission = self._translate(_(u"You don't have permission to add this content in this place.")),
            ul_error_disallowed_type = self._translate(_(u"This type of element is not allowed in this folder.",)),
            ul_error_already_exists = self._translate(_(u"This file already exists with the same name on server:")),
            ul_error_zodb_conflict = self._translate(_(u"A data base conflict error happened when uploading this file:")),
            ul_error_server        = self._translate(_(u"Server error, please contact support and/or try again.")),
        )

        settings['typeupload'] = typeupload
        if typeupload:
            imageTypes = _listTypesForInterface(context, 'image')
            if typeupload in imageTypes:
                ul_content_types_infos = self.ul_content_types_infos('image')
            else:
                ul_content_types_infos = self.ul_content_types_infos(
                    mediaupload
                )
        else:
            ul_content_types_infos = self.ul_content_types_infos(mediaupload)

        settings['ul_file_extensions'] = ul_content_types_infos[0]
        settings['ul_file_extensions_list'] = str(ul_content_types_infos[1])
        settings['ul_file_description'] = ul_content_types_infos[2]

        return settings

    def use_flash_as_fallback(self):
        # Use flash as fallback if xhr multiupload is not available
        # Currently this affects only IE < 10
        user_agent = self.request.get_header('User-Agent')
        fallback = self.qup_prefs.use_flash_as_fallback

        return not can_dnd(user_agent) and fallback

    def __call__(self, for_id="uploader"):
        self.uploader_id = for_id
        settings = self.upload_settings()

        if self.qup_prefs.use_flashupload or self.use_flash_as_fallback():
            return FLASH_UPLOAD_JS % settings
        return XHR_UPLOAD_JS % settings


class QuickUploadAuthenticate(BrowserView):
    """
    base view for quick upload authentication
    ticket is used only with flash upload
    nothing is done with xhr upload.
    Note: we don't use the collective.uploadify method
    for authentication because sending cookie in all requests
    is not secure.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        portal = getUtility(IPloneSiteRoot)
        self.qup_prefs = IQuickUploadControlPanel(portal)
        self.use_flashupload = self.qup_prefs.use_flashupload

    def _auth_with_ticket(self):
        """
        with flashupload authentication is done using a ticket
        """

        context = aq_inner(self.context)
        request = self.request
        url = context.absolute_url()

        ticket = getDataFromAllRequests(request, 'ticket')
        if ticket is None:
            raise Unauthorized('No ticket specified')

        logger.info('Authenticate using ticket, the ticket is "%s"' % ticket)
        username = ticketmod.ticketOwner(url, ticket)
        if username is None:
            logger.info('Ticket "%s" was invalidated, cannot be used '
                        'any more.' % str(ticket))
            raise Unauthorized('Ticket is not valid')

        self.old_sm = SecurityManagement.getSecurityManager()
        user = find_user(context, username)
        SecurityManagement.newSecurityManager(self.request, user)
        logger.info('Switched to user "%s"' % username)


class QuickUploadFile(QuickUploadAuthenticate):
    """ Upload a file
    """

    def __call__(self):
        """
        """
        if self.use_flashupload:
            return self.flash_upload_file()
        return self.quick_upload_file()

    def flash_upload_file(self):

        context = aq_inner(self.context)
        request = self.request
        self._auth_with_ticket()

        file_name = request.form.get("Filename", "")
        file_data = request.form.get("Filedata", None)
        content_type = get_content_type(context, file_data, file_name)
        portal_type = request.form.get('typeupload', '')
        title = request.form.get("title", None)
        description = request.form.get("description", None)

        if not portal_type:
            ctr = getToolByName(context, 'content_type_registry')
            portal_type = ctr.findTypeName(
                file_name.lower(), content_type, '') or 'File'

        if file_data:
            factory = IQuickUploadFileFactory(context)
            logger.debug(
                "Uploading file with flash: filename=%s, title=%s, "
                "description=%s, content_type=%s, portal_type=%s" % (
                    file_name, title, description, content_type, portal_type))

            try:
                f = factory(
                    file_name,
                    title,
                    description,
                    content_type,
                    file_data,
                    portal_type
                )
            except:
                raise
            if f['success'] is not None:
                o = f['success']
                logger.info("file url: %s" % o.absolute_url())
                SecurityManagement.setSecurityManager(self.old_sm)
                return o.absolute_url()

    def quick_upload_file(self):
        context = aq_inner(self.context)
        request = self.request
        response = request.RESPONSE

        response.setHeader('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT')
        response.setHeader('Cache-control', 'no-cache')
        # the good content type woul be text/json or text/plain but IE
        # do not support it
        response.setHeader('Content-Type', 'text/html; charset=utf-8')
        # disable diazo themes
        request.response.setHeader('X-Theme-Disabled', 'True')

        if request.HTTP_X_REQUESTED_WITH:
            # using ajax upload
            file_name = urllib.unquote(request.HTTP_X_FILE_NAME)
            upload_with = "XHR"
            try:
                file = request.BODYFILE
                file_data = file.read()
                file.seek(0)
            except AttributeError:
                # in case of cancel during xhr upload
                logger.error("Upload of %s has been aborted", file_name)
                # not really useful here since the upload block
                # is removed by "cancel" action, but
                # could be useful if someone change the js behavior
                return json.dumps({u'error': u'emptyError'})
            except:
                logger.error(
                    "Error when trying to read the file %s in request",
                    file_name
                )
                return json.dumps({u'error': u'serverError'})
        else:
            # using classic form post method (MSIE<=8)
            file = request.get("qqfile", None)
            file_data = file.read()
            file.seek(0)
            filename = getattr(file, 'filename', '')
            file_name = filename.split("\\")[-1]
            try:
                file_name = file_name.decode('utf-8')
            except UnicodeDecodeError:
                pass

            file_name = IUserPreferredFileNameNormalizer(
                self.request
            ).normalize(file_name)
            upload_with = "CLASSIC FORM POST"
            # we must test the file size in this case (no client test)
            if not self._check_file_size(file):
                logger.info("Test file size: the file %s is too big, upload "
                            "rejected" % filename)
                return json.dumps({u'error': u'sizeError'})

        # overwrite file
        try:
            newid = get_id_from_filename(
                file_name, context, unique=self.qup_prefs.object_unique_id)
        except MissingExtension:
            return json.dumps({u'error': u'missingExtension'})

        if (newid in context or file_name in context) and not self.qup_prefs.object_unique_id:
            updated_object = context.get(newid, False) or context[file_name]
            mtool = getToolByName(context, 'portal_membership')
            override_setting = self.qup_prefs.object_override
            if override_setting and\
                    mtool.checkPermission(ModifyPortalContent, updated_object):
                can_overwrite = True
            else:
                can_overwrite = False

            if not can_overwrite:
                logger.debug(
                    "The file id for %s already exists, upload rejected"
                    % file_name
                )
                return json.dumps({u'error': u'serverErrorAlreadyExists'})

            overwritten_file = updated_object
        else:
            overwritten_file = None

        content_type = get_content_type(context, file_data, file_name)

        portal_type = getDataFromAllRequests(request, 'typeupload') or ''
        title = getDataFromAllRequests(request, 'title') or ''
        description = getDataFromAllRequests(request, 'description') or ''

        if not portal_type:
            ctr = getToolByName(context, 'content_type_registry')
            portal_type = ctr.findTypeName(
                file_name.lower(), content_type, ''
            ) or 'File'

        if file_data:
            if overwritten_file is not None:
                updater = IQuickUploadFileUpdater(context)
                logger.info(
                    "reuploading %s file with %s: title=%s, description=%s, "
                    "content_type=%s"
                    % (overwritten_file.absolute_url(), upload_with, title,
                       description, content_type))
                try:
                    f = updater(overwritten_file, file_name, title,
                                description, content_type, file_data)
                except ConflictError:
                    # Allow Zope to retry up to three times, and if that still
                    # fails, handle ConflictErrors on client side if necessary
                    raise
                except Exception, e:
                    logger.error(
                        "Error updating %s file: %s", file_name, str(e)
                    )
                    return json.dumps({u'error': u'serverError'})

            else:
                factory = IQuickUploadFileFactory(context)
                logger.info(
                    "uploading file with %s: filename=%s, title=%s, "
                    "description=%s, content_type=%s, portal_type=%s"
                    % (upload_with, file_name, title,
                       description, content_type, portal_type))
                try:
                    f = factory(file_name, title, description, content_type,
                                file_data, portal_type)
                except ConflictError:
                    # Allow Zope to retry up to three times, and if that still
                    # fails, handle ConflictErrors on client side if necessary
                    raise
                except Exception, e:
                    logger.error(
                        "Error creating %s file: %s", file_name, str(e)
                    )
                    return json.dumps({u'error': u'serverError'})

            if f['success'] is not None:
                o = f['success']
                logger.info("file url: %s" % o.absolute_url())
                if HAS_UUID:
                    uid = IUUID(o)
                else:
                    uid = o.UID()

                msg = {
                    u'success': True,
                    u'uid': uid,
                    u'name': o.getId(),
                    u'title': o.pretty_title_or_id()
                }
            else:
                msg = {u'error': f['error']}
        else:
            msg = {u'error': u'emptyError'}

        return json.dumps(msg)

    def _check_file_size(self, data):
        max_size = int(self.qup_prefs.size_limit)
        if not max_size:
            return 1

        #file_size = len(data.read()) / 1024
        data.seek(0, os.SEEK_END)
        file_size = data.tell() / 1024
        data.seek(0, os.SEEK_SET)
        max_size = int(self.qup_prefs.size_limit)
        if file_size <= max_size:
            return 1

        return 0


def get_content_type(context, file_data, filename):
    if isinstance(file_data, FileUpload):
        file_data = file_data.read()
    content_type = mimetypes.guess_type(filename)[0]
    # sometimes plone mimetypes registry could be more powerful
    if not content_type:
        mtr = getToolByName(context, 'mimetypes_registry')
        mimetype = mtr.classify(file_data, filename=filename)
        if mimetype is not None:
            return str(mimetype)

    return content_type


class QuickUploadCheckFile(BrowserView):
    """
    check if file exists
    """

    def quick_upload_check_file(self):

        context = aq_inner(self.context)
        request = self.request

        already_exists = {}
        formdict = request.form
        ids = context.objectIds()

        for k, v in formdict.items():
            if k != 'folder':
                if v in ids:
                    already_exists[k] = v

        return str(already_exists)

    def __call__(self):
        """
        """
        return self.quick_upload_check_file()
