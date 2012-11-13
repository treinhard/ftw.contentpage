from ftw.contentpage.testing import FTW_CONTENTPAGE_FUNCTIONAL_TESTING
from unittest2 import TestCase
from simplelayout.base.interfaces import ISimpleLayoutBlock
from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from zope.component import queryMultiAdapter
from StringIO import StringIO
import transaction


class TestListingBlockCreation(TestCase):

    layer = FTW_CONTENTPAGE_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestListingBlockCreation, self).setUp()
        self.portal = self.layer['portal']
        self.portal_url = self.portal.portal_url()

        self.contentpage = self.portal.get(
            self.portal.invokeFactory('ContentPage', 'contentpage'))
        # Fire all necessary events
        self.contentpage.processForm()
        transaction.commit()

        # Browser setup
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False

    def _auth(self):
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (
            TEST_USER_NAME, TEST_USER_PASSWORD, ))

    def _create_listingblock(self):
        listingblock = self.contentpage.get(
            self.contentpage.invokeFactory('ListingBlock', 'listingblock'))
        # Fire all necessary events
        listingblock.processForm()
        transaction.commit()
        return listingblock

    def test_fti(self):
        self.assertIn('ListingBlock', self.portal.portal_types.objectIds())

    def test_creation(self):
        _id = self.contentpage.invokeFactory('ListingBlock', 'listingblock')
        self.assertIn(_id, self.contentpage.objectIds())

    def test_simplelayout_integration(self):
        listingblock = self._create_listingblock()
        ISimpleLayoutBlock.providedBy(listingblock)

    def test_listingblock_view(self):
        listingblock = self._create_listingblock()
        self._auth()
        self.browser.open(self.contentpage.absolute_url())
        self.assertIn(listingblock.getId(), self.browser.contents)
        self.assertIn('simplelayout-block-wrapper ListingBlock',
                      self.browser.contents)

    def test_listing_block_table_render(self):
        listingblock = self._create_listingblock()
        _file = listingblock.get(
            listingblock.invokeFactory('File', 'file'))
        dummy = StringIO("DATA")
        dummy.filename = 'dummy.pdf'
        _file.setFile(dummy)
        _file.setTitle("Dummy PDF")
        _file.processForm()

        view = queryMultiAdapter((listingblock, listingblock.REQUEST),
                                 name='block_view')
        self.assertIn("Dummy PDF", view.render_table())
        self.assertIn("pdf.png", view.render_table())

    def test_addressblock_default_title(self):
        listingblock = self._create_listingblock()
        self.assertEquals('Downloads', listingblock.Title())

        self._auth()
        self.browser.open(self.contentpage.absolute_url())
        self.assertIn('<h2>Downloads', self.browser.contents)

    def test_exclude_from_nav(self):
        listingblock = self._create_listingblock()
        self.assertTrue(listingblock.getExcludeFromNav())

    def tearDown(self):
        super(TestListingBlockCreation, self).tearDown()
        portal = self.layer['portal']
        portal.manage_delObjects(['contentpage'])

        transaction.commit()