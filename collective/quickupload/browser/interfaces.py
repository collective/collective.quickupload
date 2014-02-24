# -*- coding: utf-8 -*-
import logging
log = logging.getLogger('collective.quickupload.interfaces')
log.warning(
    "Importing interfaces from collective.quickupload.browser.interfaces is "
    "deprecated, please import from collective.quickupload.interfaces"
)

from collective.quickupload.interfaces import IQuickUploadCapable  # nopep8
from collective.quickupload.interfaces import IQuickUploadNotCapable  # nopep8
from collective.quickupload.interfaces import IQuickUploadFileFactory  # nopep8
