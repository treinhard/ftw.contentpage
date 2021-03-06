from ftw.contentpage import config
from ftw.contentpage.testing import FTW_CONTENTPAGE_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.testing.z2 import Browser
from Products.CMFCore.utils import getToolByName
from simplelayout.base.views import SimpleLayoutView
from unittest2 import TestCase
from zope.viewlet.interfaces import IViewletManager


from zope.component import queryMultiAdapter
import transaction


class TestContentListing(TestCase):

    layer = FTW_CONTENTPAGE_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestContentListing, self).setUp()
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

    def _get_viewlet(self):
        view = SimpleLayoutView(self.contentpage, self.contentpage.REQUEST)
        manager_name = 'simplelayout.base.listing'
        manager = queryMultiAdapter(
            (self.contentpage, self.contentpage.REQUEST, view),
            IViewletManager,
            manager_name)
        self.failUnless(manager)
        # Set up viewlets
        manager.update()
        name = 'ftw.contentpage.contentlisting'
        return [v for v in manager.viewlets if v.__name__ == name]

    def test_component_registered(self):
        self.assertTrue(len(self._get_viewlet()) == 1)

    def test_category_field(self):
        self.assertIn('content_categories', self.contentpage.Schema())
        self.contentpage.Schema()['content_categories'].set(
            self.contentpage, 'DEMO1')
        self.assertEquals(
            self.contentpage.Schema()['content_categories'].get(
                self.contentpage),
            ('DEMO1',))

    def test_category_index(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        for name, meta_type in config.INDEXES:
            self.assertIn(name, catalog.indexes())

        subpage = self.contentpage.get(
            self.contentpage.invokeFactory('ContentPage', 'subpage'))
        subpage.processForm()
        subpage.setTitle('Subpage title')
        subpage.Schema()['content_categories'].set(subpage, 'DEMO1')
        subpage.reindexObject()
        self.assertTrue(catalog({'content_categories': 'DEMO1'})[0])

    def test_category_index_umlauts(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        subpage = self.contentpage.get(
            self.contentpage.invokeFactory('ContentPage', 'subpage'))
        subpage.processForm()
        subpage.setTitle('Subpage title')
        subpage.Schema()['content_categories'].set(
            subpage, 'WITH UTF8 \xc3\xa4')
        subpage.reindexObject()
        unique_values = catalog.Indexes['getContentCategories'].uniqueValues()
        self.assertIn("WITH UTF8 \xc3\xa4", unique_values)

    def test_viewlet(self):
        viewlet = self._get_viewlet()[0]
        # Should be empty
        self.assertFalse(viewlet.available())
        # Create more content
        subpage = self.contentpage.get(
            self.contentpage.invokeFactory(
                'ContentPage', 'subpage', description='SubpageDescription'))
        subpage.setTitle('Subpage')
        # Test with umlauts
        subpage.Schema()['content_categories'].set(
            subpage, '\xc3\xa4u\xc3\xa4')
        subpage.reindexObject()
        subpage2 = self.contentpage.get(
            self.contentpage.invokeFactory('ContentPage', 'subpage2'))
        subpage2.setTitle('Subpage2')
        subpage2.Schema()['content_categories'].set(subpage2, 'DEMO2')
        subpage2.reindexObject()
        subpage3 = self.contentpage.get(
            self.contentpage.invokeFactory(
                'ContentPage', 'subpage3', description='OtherDescription'))
        subpage3.setTitle('Subpage3')
        subpage3.Schema()['content_categories'].set(subpage3, 'DEMO2')
        subpage3.reindexObject()

        viewlet = self._get_viewlet()[0]
        self.assertTrue(viewlet.available())
        self.assertEquals(
            viewlet.get_content(),
            [('\xc3\xa4u\xc3\xa4',
                [('Subpage', subpage.absolute_url(), 'SubpageDescription')]),
             ('DEMO2',
                [('Subpage2', subpage2.absolute_url(), 'Subpage2'),
                 ('Subpage3', subpage3.absolute_url(), 'OtherDescription')])])
        transaction.commit()
        self._auth()
        self.browser.open(self.contentpage.absolute_url())
        self.assertIn('\xc3\xa4u\xc3\xa4', self.browser.contents)
        self.assertIn('DEMO2', self.browser.contents)
        self.assertIn('subelements-listing-element', self.browser.contents)

    def tearDown(self):
        super(TestContentListing, self).tearDown()
        portal = self.layer['portal']
        portal.manage_delObjects(['contentpage'])
        transaction.commit()
