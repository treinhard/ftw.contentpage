PROJECTNAME = 'ftw.contentpage'


ADD_PERMISSIONS = {
    'ContentPage': 'ftw.contentpage: Add ContentPage',
    'AddressBlock': 'ftw.contentpage: Add AddressBlock',
    'ListingBlock': 'ftw.contentpage: Add ListingBlock',
    'TextBlock': 'ftw.contentpage: Add TextBlock',
    'News': 'ftw.contentpage: Add News',
    'NewsFolder': 'ftw.contentpage: Add NewsFolder',
}

INDEXES = (('getContentCategories', 'KeywordIndex'),
          ('getContentType', 'FieldIndex'))


ORIGINAL_SIZE = (900, 900)
