from collective.geo.settings.interfaces import IGeoCustomFeatureStyle
from zope.component import queryAdapter


def initializeCustomFeatureStyles(obj, event):
    """Initializes IGeoCustomFeatureStyle for OrgUnits upon object creation.

    For OrgUnits we don't want to display the map viewlet in one of the default
    viewlet managers but only in the custom 'contact_view'.
    """
    custom_styles = queryAdapter(obj, IGeoCustomFeatureStyle)
    custom_styles.set('use_custom_styles', True)
    custom_styles.set('map_viewlet_position', 'fake-manager')  # Don't display
