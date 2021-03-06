from AccessControl import ClassSecurityInfo
from ftw.contentpage.config import PROJECTNAME
from ftw.contentpage.interfaces import ICategorizable
from ftw.contentpage.interfaces import IContentPage
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from simplelayout.base.interfaces import IAdditionalListingEnabled
from simplelayout.base.interfaces import ISimpleLayoutCapable
from zope.interface import implements
from Acquisition import aq_parent
from Acquisition import aq_inner
from Products.CMFCore.permissions import View

from Products.ATContentTypes.config import HAS_LINGUA_PLONE
if HAS_LINGUA_PLONE:
    from Products.LinguaPlone import public as atapi
else:
    from Products.Archetypes import atapi


ContentPageSchema = folder.ATFolderSchema.copy()

schemata.finalizeATCTSchema(
    ContentPageSchema,
    folderish=True,
    moveDiscussion=False,
)


class ContentPage(folder.ATFolder):
    """A simplelayout content page"""
    implements(IContentPage, ICategorizable, ISimpleLayoutCapable,
               IAdditionalListingEnabled)

    meta_type = "ContentPage"
    schema = ContentPageSchema
    security = ClassSecurityInfo()

    security.declarePublic('canSetDefaultPage')
    def canSetDefaultPage(self):
        return False

    security.declareProtected(View, 'getAvailableLayouts')
    def getAvailableLayouts(self):
        result = super(ContentPage, self).getAvailableLayouts()
        parent = aq_parent(aq_inner(self))
        mid = 'authorities_view'
        # authorities_view is only possible on certain points
        # For example if the ContentPage is created on plone-root.
        # This changes the Plone default behaveiour off setting the layout
        # property on child objects. We don't want this, so let's check for
        # the parent meta_type
        if parent.meta_type == self.meta_type:
            result.remove((mid, mid))
        return result


atapi.registerType(ContentPage, PROJECTNAME)
