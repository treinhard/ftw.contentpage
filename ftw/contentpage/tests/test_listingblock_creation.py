from ftw.contentpage.testing import FTW_CONTENTPAGE_INTEGRATION_TESTING
from plone.registry.interfaces import IRegistry
from simplelayout.base.interfaces import ISimpleLayoutBlock
from unittest2 import TestCase
from zope.component import getUtility
from plone.registry import Record, field


class TestListingBlockCreation(TestCase):

    layer = FTW_CONTENTPAGE_INTEGRATION_TESTING

    def setUp(self):
        super(TestListingBlockCreation, self).setUp()
        self.portal = self.layer['portal']
        self.portal_url = self.portal.portal_url()

        self.contentpage = self.portal.get(
            self.portal.invokeFactory('ContentPage', 'contentpage'))
        # Fire all necessary events
        self.contentpage.processForm()

    def _create_listingblock(self):
        listingblock = self.contentpage.get(
            self.contentpage.invokeFactory('ListingBlock', 'listingblock'))
        # Fire all necessary events
        listingblock.processForm()

        return listingblock

    def test_fti(self):
        self.assertIn('ListingBlock', self.portal.portal_types.objectIds())

    def test_creation(self):
        _id = self.contentpage.invokeFactory('ListingBlock', 'listingblock')
        self.assertIn(_id, self.contentpage.objectIds())

    def test_simplelayout_integration(self):
        listingblock = self._create_listingblock()
        ISimpleLayoutBlock.providedBy(listingblock)

    def test_exclude_from_nav(self):
        listingblock = self._create_listingblock()
        self.assertTrue(listingblock.getExcludeFromNav())

    def test_get_columns(self):
        listingblock = self._create_listingblock()
        self.assertEquals(listingblock.getColumns().keys(),
                          ['getContentType', 'Title', 'modified', 'Creator',
                           'getObjSize'])
        self.assertEquals(listingblock.getColumns().values(),
                          ['column_type', 'column_title', 'column_modified',
                           'column_creater', 'column_size'])

    def test_default_title(self):
        listingblock = self._create_listingblock()
        # Default is empty
        self.assertEquals(None, listingblock.Title())

    def test_change_default_title(self):
        registry = getUtility(IRegistry)
        registry.records['ftw.contentpage.listingblock.defaulttitle'] = \
            Record(field.TextLine(title=u"dummy", default=u"N/A"),
                   value=u'Downloads')

        listingblock = self._create_listingblock()
        self.assertEquals('Downloads', listingblock.Title())

    def tearDown(self):
        super(TestListingBlockCreation, self).tearDown()
        portal = self.layer['portal']
        portal.manage_delObjects(['contentpage'])
