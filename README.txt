Description
===========
This product offers a files quick upload tool for Plone, with multi selection,
drag and drop, progress bar ....

To install it in your buildout, just add 'collective.quickupload' to your egg list.

To install it in Plone, use the add ons control panel, select the Quick Upload Product
and install it.

To see it in action, just assign the Quick Upload portlet somewhere in your site
and test it.

Details
=======

This package contains :

collective.quickupload.browser
------------------------------

 -  A simple ajax view that can be called by any plone template.
    
 -  the view is using a javascript multiple upload tool based on fileuploader.js (a fork with some ameliorations of 
    http://valums.com/ajax-upload/) OR jquery.uploadify (based on flashupload see also collective.uploadify)
    
    - By default the javascript only method is used : the fileuploader.js is a pure ajax file uploader which uses
      html5 multiple file fields and ajax upload post method. It's not a jquery plugin. For modern browsers
      like FireFox 3.6+, Chrome, or Safari 4+, it offers drag and drop, multi selection, and progress bar during upload.
      For other browsers (IE7, IE8, ...),  the script offers a graceful hidden iframe upload fall back.
      
    - Flashupload (jquery.uploadify) is more user friendly under MSIE, but has some problems :

      - not standard (use Flash)
       
      - cannot be used through https
       
      - cannot be used behind any kind of http authentication (basic authentication, windowsNT authentication, ...)

    - the webmaster has the choice between these 2 solutions (see control panel below).

    - the upload form can be viewed only with permission CMF.AddPortalContent on context
  
    - the upload form can be viewed  only for objects providing IQuickUploadCapable, by default ATFolder, ATBTreeFolder and Plone Site
      are implementing IQuickUploadCapable
  
    - the quickupload form allows to fill title for each uploaded file (see control panel below)
  
    - the quickupload view log and returns errors to the form (unauthorized, id always exist, type not allowed, etc ... )
  
    - the view can use some attributes set in session or request::
      
      -  force mediatype (could be None, image, video, audio)
         
         if a mediatype is set in request :
          
          -  an error will be raised in the form when the file content-type selected is not correct, when using the hidden iframe method.
        
          -  Flashupload is more user friendly : only choosed content types are shown in selection  window, 
             with a specific message "select images", "select video files" (...).
  
      -  force portal_type
  
         if no portal_type is set in request, content_type_registry is used to find the good portal_type, otherwise the "File" portal_type will be used.

 - a basic Plone Control panel with some options::

    - use flashupload (yes/no), default = no

    - show titles fields in form (yes/no), default = no

    - automatic upload on select (yes/no), default=yes
    
    - max size limit for each file in KB (default= 0 = no limit)
       

collective.quickupload.portlet
------------------------------

 - a portlet calling the quickupload ajax view (just an example of how to use the ajax view)

 - the portlet is not assigned (can be done TTW or in another package)


collective.quickupload.profiles
-------------------------------

 - control panel GS profile

 - the javascript and css registry GS profile
 
 - portlet GS profile


quickupload.tests
-----------------

 - test control panel and portlet

 - test the upload of a file (different use cases and errors)


How To
======

- How to add the quickupload view in my own template or viewlet ?

  Just look the quickupload portlet code, it's easy.
  
  You can also take a look at collective.plonefinder product which uses
  collective.quickupload.


More Information
================

Contact me : jeanmat.grimaldi at gmail.com

