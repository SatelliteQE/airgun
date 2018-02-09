from widgetastic.widget import View

from ..widgets import HorizontalNavigation


class BaseLoggedInView(View):
    navigation = HorizontalNavigation()
