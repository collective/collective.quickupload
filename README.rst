.. image:: https://travis-ci.org/collective/collective.quickupload.png?branch=master
   :target: https://travis-ci.org/collective/collective.quickupload

==================
Plone Quick Upload
==================

Description
===========
This product offers a multiple files upload tool for Plone, with multi
selection, drag and drop, and progress bar. A pure javacript tool is used on
client side, with html5 file fields and ajax upload for modern browsers, and a
graceful fallback for other browsers. You can also choose to replace the
javascript with jquery.uploadify, a flashupload based script which could be
interesting in rare situations (Plone site for MSIE client's browsers only,
without http authentication in front, and no https).

To install it in your buildout, just add 'collective.quickupload' to your egg
list, then::

    $ bin/buildout

To install it in Plone, use the Addons control panel, select
"Plone Quick Upload" Product and install it.

To see it in action, just assign the Quick Upload portlet somewhere in your
site and test it.

Details
=======

This package contains:

collective.quickupload.browser
------------------------------

- A simple ajax view that can be called by any plone template.

- This view is using a javascript multiple upload tool based on fileuploader.js
  (a fork with many ameliorations of
  http://valums.com/ajax-upload/) OR jquery.uploadify.js (based on flashupload,
  see also collective.uploadify plone product from which some parts of code
  have been taken)

- By default the javascript only method is used : the fileuploader.js is a pure
  ajax file uploader which uses html5 multiple file fields and ajax upload post
  method. It's not a jquery plugin. For modern browsers like FireFox 3.6+,
  Chrome, or Safari 4+, it offers drag and drop, multi-selection, and progress
  bar during upload. For other browsers (IE7, IE8, ...),  the script offers a
  graceful hidden iframe upload fall back.

  - Flashupload (jquery.uploadify) is more user friendly under MSIE, but has
    some "big" problems:

    - cannot be used behind any kind of http authentication
      (basic authentication, windowsNT authentication, ...)

    - cannot be used through https

    - not open source

  - the webmaster has the choice between these 2 solutions (see control panel
    below).

  - the upload form can be viewed only with permission CMF.AddPortalContent on
    context

  - the upload form can be viewed  only for objects providing
    IQuickUploadCapable, by default ATFolder, ATBTreeFolder and Plone Site are
    implementing IQuickUploadCapable

  - the quickupload form allows to fill title and description for each uploaded
    file (see control panel below)

  - the quickupload view log and returns errors to the form (unauthorized, id
    always exist, type not allowed, etc ... )

  - the view can use some attributes set in session or request:

    - force mediatype (could be None, image, video, audio, or something like
      this '*.pdf;*.doc;')

      if a mediatype is set in request :

      - with fileuploader.js an error is raised in the form when a file
        content-type selected is not correct.

        - with Flashupload, only choosed content types are shown in selection
          window, with a specific message "select images", "select video files"
          (...).

      - force portal_type

        if portal_type is not set in request, content_type_registry is used to
        find the good portal_type, otherwise the "File" portal_type will be
        used.

  - a basic Plone Control panel with some options:

    - use flashupload (yes/no), default = no

    - fill file's titles in form (yes/no), default = yes

    - fill file's descriptions in form (yes/no), default = no

    - automatic upload on select (yes/no), default=no

    - max size limit for each file in KB (default= 0 = no limit)

    - simultaneous uploads limit (default=2, 0 = no limit)


collective.quickupload.portlet
------------------------------

- a portlet calling the quickupload ajax view (it's also an example on how to
  use the quick_upload view)

- the portlet is not assigned (can be done TTW or in another package)


collective.quickupload.profiles
-------------------------------

- control panel GS profile

- the javascript and css registry GS profile

- portlet GS profile


quickupload.tests
-----------------

- doctests for control panel, portlet, and quick_upload view


Compliance
==========

- Plone 4.3
- Plone 4.2
- Plone 4.1

Plone 4.0 support stopped with 1.6.0, Plone 3.3.x support stopped with 1.0.3.


About fileuploader.js fork
==========================

These ameliorations have been done:

- queue uploads

- graphic progress bar

- simultaneous upload limit

- can send all files in a second time, after multiple selections, and after
  different actions on form.

- can add new fields using a new method (onAfterSelect), associated to each file

- debugMode and debugConsole

- css improvements


How To
======

- How to add the quickupload view in my own template or viewlet?

  Just look the quickupload portlet code, it's really easy.

  You can also take a look at collective.plonefinder product
  http://plone.org/products/collective.plonefinder
  which requires collective.quickupload.

- How to set by code types where upload is allowed ?

  You include minimal.zcml only, adding to your product configure.zcml::

      <exclude package="collective.quickupload" file="configure.zcml" />
      <include package="collective.quickupload" file="minimal.zcml" />

  And you implement IUploadCapable on types you want::

      <class class=".content.EPRIVR_Documents.EPRIVR_Domain">
        <implements interface="collective.quickupload.browser.interfaces.IQuickUploadCapable" />
      </class>

- How to exclude upload on some types ?

  If a type implements IQuickUploadNotCapable, portlet will never be shown on it.
  Add to your zcml::

      <class class=".content.MyContent">
        <implements interface="collective.quickupload.browser.interfaces.IQuickUploadNotCapable" />
      </class>

TODO
====

- javascript client tests

- unit tests for upload methods

- fileuploader.js refactorisation using jquery

- add tests for upload viewlet

- pep8/code cleanup

- set default values to show upload button after install

- WTF confusing docs?


Support
=======

Please file all tickets to issue page on github
https://github.com/collective/collective.quickupload/issues.


Repository
==========

https://github.com/collective/collective.quickupload/


More Information
================

Jean-mat Grimaldi http://macadames.wordpress.com

Thanks to :

- Adrew Valumns (for original fileuploader.js),
- Ramon Bartl (for some parts of code taken in collective.uploadify Plone product),
- Ronnie Garcia, Travis Nickels (for jquery.uploadify.js)
- Gilles Lenfant David Pack and Christophe Combelles, Alter Way Solutions,
  for functional tests, ideas, and moral support.
- Maik Roeder, for functional tests
- Thomas Desvenain, current maintainer
- Daniel Widerin
- Wolfgang Thomas
