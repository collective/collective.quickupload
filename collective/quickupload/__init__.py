"""Main product initializer
"""

import logging
from zope.i18n import MessageFactory
logger = logging.getLogger("collective.quickupload")

siteMessageFactory = MessageFactory("collective.quickupload")

def initialize(context):
    """Initializer called when used as a Zope 2 product."""