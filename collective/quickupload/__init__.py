"""Main product initializer
"""

import logging
import pkg_resources
from zope.i18n import MessageFactory


try:
    pkg_resources.get_distribution('plone.dexterity')
except pkg_resources.DistributionNotFound:
    HAS_DEXTERITY = False
else:
    HAS_DEXTERITY = True

logger = logging.getLogger("collective.quickupload")

siteMessageFactory = MessageFactory("collective.quickupload")


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
