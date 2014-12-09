Changelog
=========

1.6.6 (2014-12-09)
------------------

- jQuery 1.9 compatible
  [vincentfretin]

- Reimplement 'copy' dopEffect for Chrome, Safari and Firefox. IE always shows
  a 'move' dropEffect.
  Check issue (https://github.com/collective/collective.quickupload/pull/47)
  for more details.
  [mathias.leimgruber]

- Fix file size check that occurs for uploads without the HTTP_X_REQUESTED_WITH
  request header set.
  [damilgra]


1.6.5 (2014-07-04)
------------------

- Use same function to detect mimetypes in flash & quick upload.
  [tschanzt]


1.6.4 (2014-06-03)
------------------

- Register QuickUploadViewlet for all skins.
  [thet]

- Make sure IObjectModifiedEvent is notified for uploaded Dexterity objects, as
  happens already with Archetypes.
  [jcbrand]

1.6.3 (2014-02-26)
------------------

- Render CSS resources as links instead of imports for better performance.
  [thet]

- More complete uninstall profile.
  [thet]

- Fix deprecated zope.app.cache import.
  [esteele]

- Fix IQuickUploadCapable uses in browser/configure.zcml to avoid to raise warning.
  [cedricmessiant]

- i18n fixes.
  [thomasdesvenain]

- Add an upgrade step to add property 'Override by upload file'.
  This fixes configuration panel after 1.6.1.
  [thomasdesvenain]


1.6.2 (2013-12-02)
------------------

- Add missing semicolon at the end of helpers.js.
  [vincentfretin]


1.6.1 (2013-10-18)
------------------

- Use the classify function of the MimetypeRegistry because it is more robust.
  [tschanzt]

- Enable DnD upload for IE > 9.
  Include fixing fileupload.js for IE 10
  [mathias.leimgruber]

- Add dutch translations
  [maartenkling]

- Add setting property, it's 'Override by upload file'
  If the folder already has same file name,
  Checked: Override, Non-Checked: raise upload error.
  [terapyon]

1.6.0 (2013-07-18)
------------------

- Added plone domain and translations
  [macagua]

- Updated catalog gettext and translations
  [macagua]

- Added more improvements about i18n
  [macagua]

- Added more i18ndude options into bash scrit
  [macagua]

- Move completly to plone.app.testing instead of mixed collective.testcaselayer
  and PloneTestCase usage.
  [saily]

- Restructure buildout
  [saily]

- Handle HTTP status code 500 explicitly.
  [durko]

- Fixed creation of dexterity-content
  (regression sneaked in via d2bf4ff)
  [till44]

- Dexterity integration
  [pysailor]

- Added viewlet as alternative to portlet for uploading
  [pysailor]

- Czech translation
  [naro]

1.5.8 (2013-01-25)
------------------

- Fixed: do not remove file extensions at upload.
  [thomasdesvenain]

- Add flash fallback for IE. Configurable throught quick upload
  control panel. It's disabled by default
  [mathias.leimgruber]


1.5.7 (2012-12-21)
------------------

- Ensure new document is not generated when a document with same id exists.
  (Fix: feature of 1.5 release didn't work when filename had characters not normalized)
  [thomasdesvenain]

- Removed trailing comma.
  [Julian Infanger]

- Fix: if auto version policy is selected for content type,
  a version is saved when we replace a file using quickupload
  (notify object edited instead of object modified).
  [thomasdesvenain]

- Slovak translation.
  [lck]

- Insert html from ajax response into portlet only on expected response.
  If the user does not have sufficient privileges, the login page is returned
  in the ajax response instead of the expected portlet content.
  [vsomogyi]

- Disabled Diazo theming in the @@quickupload view.
  [dokai]

- Update German translations.
  [jone]

- made it work with plone 4.3 (import changed)
  [jensens, bennyboy]

- updated italian translation
  [keul]

- do not create ``SESSION`` object when not needed (see #21)
  [keul]

1.5.6 (2012-10-09)
------------------

- Dexterity-related fixes.
  [till44]

- Updated po files and french translation.
  [thomasdesvenain]

- Updated italian translation.
  [giacomos]


1.5.5 (2012-08-25)
------------------

- Added a specific error message if upload failed
  because content type is disallowed in the folder.
  [thomasdesvenain]


1.5.4 (2012-08-17)
------------------

- Remove creation flag once content has been created
  and file loaded.
  [thomasdesvenain]

- Updated zh-tw and it translations.
  [l34marr, giacomos]

1.5.3 (2012-07-13)
------------------

- Fixed title generation
  if we have more than one "." character in file name.
  Fixes http://plone.org/products/collective.quickupload/issues/24
  [Manuel Reinhart, thomasdesvenain]

- Portlet form doesn't break
  when a content type implements IFileContent and IImageContent.
  Fixes http://github.com/collective/collective.quickupload/issues/9.
  [vito80ba, thomasdesvenain]

- Works without plone.uuid
  (for example with a Plone 4.0.x basic install).
  [frisi, do3cc, thomasdesvenain]

- Updated chinese translation.
  [jianaijun]


1.5.2 (2012-06-29)
------------------

- Better error message when MissingExtension error.
  [thomasdesvenain]

- Fixed upload when filename has special characters under IE.
  [thomasdesvenain]


1.5.1 (2012-05-24)
------------------

- Fixed Spanish language code.
  [thomasdesvenain]

1.5 (2012-05-24)
----------------

- Use IUUID adapter instead of UID method in order to make it work also
  with Dexterity items.
  [avoinea]

- We can update existing files through quickupload.
  If user try to upload a file that already exists,
  if he is allowed to modify this existing object,
  the file, title and description fields are replaced with new values.
  [thomasdesvenain]

- German translations completed.
  [mathias.leimgruber]

- Raises MissingExtension exception when filename does not have the extension.
  [taito]

1.4 (2012-03-14)
----------------

- Fix CSS images for sites using virtual host _vh_ components.
  [dokai]

- Hide buttons after clearing the queue.
  [giacomos]

- Trigger custom JS events after each file upload and also when all files
  were uploaded
  [avoinea]

- Updated responseJSON with more info about the uploaded file
  (uid, title and name)
  [avoinea]

- More robust check for existing file with same id.
  Avoid some unsuitable error messages.
  [thomasdesvenain]

- Move interfaces to collective.quickupload.interfaces module.
  [thomasdesvenain]

- Finnish translation
  [saffe]

1.3.1 (2011-12-22)
------------------

- Display quickupload portlet on display views only
  (disable it on edit forms, etc).
  [thomasdesvenain]

- Add error logs when failures happen.
  [thomasdesvenain]

- Works with dexterity AND without blobs.
  [thomasdesvenain]


1.3.0 (2011-11-29)
------------------

- Added Italian translation
  [giacomos]

- Make sure that the portlet is rendered if upload_portal_type is set to auto.
  [swampmonkey]

- Prevent diazo themes from theming the json response.
  [swampmonkey]

- If downloaded content type has been selected in portlet settings
  and content type can't been added in current folder,
  portlet is hidden.
  [thomasdesvenain]

- Works with dexterity.
  We can upload dexterity content types which have a file or image field.
  We can upload contents in dexterity containers.
  [thomasdesvenain]

- Updated Chinese translation.
  [jianaijun]

1.2.1 (2011-10-10)
------------------

- Don't speak about drag and drop feature if navigator is IE.
  (it doesn't works unless version is IE 9.)
  [thomasdesvenain]

- If chameleon is installed the i18n:attributes don't get translated if the
  tag doesn't already have the attribute(s).
  [swampmonkey]

- Update with more Norwegian translations.
  [tormod, hannosch]

1.2.0 (2011-09-22)
------------------

* Fixed error message when trying to upload a file which already exists in folder.
  [thomasdesvenain]

* Added support for tests using plone.app.testing; control panel is now
  removed when package is uninstalled.
  [hvelarde]

* Catch errors if sessions are disabled.
  [swampmonkey]

* Use ``plone.app.portlets.ManagePortlets`` permission, allows site-admins
  to add/edit the portlet.
  [ggozad]

* A folder type can implement IQuickUploadNotCapable
  so that upload is not allowed on it.
  [thomasdesvenain]

* We can include minimal.zcml file only to manually set IUploadCapable types.
  [thomasdesvenain]

* Add more messages into po files + french translations.
  [thomasdesvenain]

* Use IQuickUploadCapable interface to test if portlet has to be displayed.
  Avoid some 404 errors.
  [thomasdesvenain]

* User defined title is internationalized in plone domain.
  [thomasdesvenain]

* Remove !important in css, that shouldn't be used in base css.
  [thomasdesvenain]

* Portlet has a bottom left and bottom right.
  [thomasdesvenain]

* Javascripts and css are loaded for authenticated users only.
  Refs http://plone.org/products/collective.quickupload/issues/11.
  [frisi, thomasdesvenain]

* Fixed portlet field validation.
  [thomasdesvenain]

* Fixed internationalizations.
  Fixed .pot and .po files.
  [thomasdesvenain]

* Added try/finally around upload_lock protected code to ensure that the lock
  is released if an exception occurs.
  [swampmonkey]

* Added Spanish translation
  [hvelarde]


1.1.1 (2011-06-27)
------------------

* Notify ObjectInializedEvent at upload.
  Fixes http://plone.org/products/collective.quickupload/issues/7
  [thomasdesvenain, thanks to lars.eisbaer]

* Pass content_type to the ContentTypeRegistry
  Fixes http://plone.org/products/collective.quickupload/issues/13/
  [thomasw]

* Added Brazilian Portuguese translation
  [erico_andrei]

* Quickupload form allows to fill description for each uploaded file
  [regisrouet]


1.1.0 (2011-04-06)
------------------

* Mimetype detection works with blobs (plone 4.0+ files).
  [thomasdesvenain]

* Keep dots in filename during id normalization.
  [thomasdesvenain]

* Plone 4.1 compatibility.
  [vincentfretin]

1.0.3
-----

* let an empty content_type when mimetype_registry return None as mimetype
  object will result in "application/octet-stream"
  macadames 2010-09-29

* use a specific interface IQuickUploadFactory in place of IFileFactory
  to avoid possible conflicts with another products using the same interface
  http://plone.org/products/collective.quickupload/issues/4
  macadames and mroeder 2010-10-07

* files id consolidation
  macadames and mroeder 2010-10-07

* log some rare exceptions (bad id, no primary field ...)
  resolve http://plone.org/products/collective.quickupload/issues/6
  macadames and mroeder 2010-10-08

* fix error in quick_upload.py when typeupload was defined without mediaupload
  resolve http://plone.org/products/collective.quickupload/issues/5
  macadames and kayeva 2010-10-10

* improve doctests (with last bugfixes on typeupload/mediaupload)
  macadames 2010-10-10

* fix doctests in Plone4
  macadames 2010-10-10

1.0.2
-----

* IE7 css fixes upload button was uggly
  macadames 2010-09-22

* fix content-type header with FireFox xhr upload
  sometimes is missing
  macadames 2010-09-24

* don't use unicode in setFileName
  because it break Archetypes File Field download (unicode decode error)
  macadames 2010-09-24

* minor fixes in medialabel for upload
  macadames 2010-09-26

1.0.1
-----

* fix set_id or check_id methods
  now called on context, no more on aq_parent(context)
  macadames 2010-09-14

* slow down the removing of progressBar
  to see something even when Plone is too fast :-)
  macadames 2010-09-15

* try to find the good content_type for uploaded files
  using plone mime_types_registry when
  mimetypes.guess_type(file_name) returns (None, None)
  macadames 2010-09-17

* fix strange ATFile behavior with content_types
  when passing mutator(data, content_type=content_type)
  the content_type is not always good
  macadames 2010-09-17

* Don't use unicode in setFileName
  macadames 2010-09-24

* fix content-type header with FireFox xhr upload
  sometimes is missing
  macadames 2010-09-24

1.0.0
-----

- fix jquery.uploadify on MSIE with a temp workaround
  see ticket : https://dev.plone.org/plone/ticket/10894
  macadames - 2010/09/02

- using different ids for each uploader methods launchers
  since we could have different uploaders in a same page
  example : an images uploader portlet, a video uploader portlet
  macadames - 2010/09/02

- remove the cookie authentication method
  with jquery.uploadify (it's not secure to send the cookie in all requests)
  Just keep the old PloneFlashUpload method (ticket)
  macadames - 2010/09/02

- many improvements around fileuploader.js (fork) :
  autoUpload option added
  onAfterSelect option added
  refactoristion with these new options
  macadames - 2010/09/02

- added fileuploader.js jscript launcher
  macadames - 2010/08/25

- change flashupload jscript launchers
  to allow multiple uploaders in same page
  macadames - 2010/08/25

- Add fileuploader.js for XHR or simple hidden iframe uploader
  macadames - 2010/08/25

- Add quick upload control panel
  macadames - 2010/08/25

- Initial release :
  extract upload code from collective.plonefinder
  to make a separate package
  macadames - 2010/08/25
