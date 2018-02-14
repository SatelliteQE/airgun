from widgetastic.widget import View

from ..widgets import HorizontalNavigation, ContextSelector


class BaseLoggedInView(View):
    navigation = HorizontalNavigation()
    context_widget = ContextSelector()
