"""Main product initializer
"""
from zope.i18n import MessageFactory
import logging
import pkg_resources

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
