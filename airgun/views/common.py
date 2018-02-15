from widgetastic.widget import View

from ..widgets import HorizontalNavigation, ContextSelector


class BaseLoggedInView(View):
    menu = HorizontalNavigation()
    taxonomies = ContextSelector()
