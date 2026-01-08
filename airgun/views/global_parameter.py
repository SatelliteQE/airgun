from widgetastic.widget import Text

from airgun.views.common import BaseLoggedInView, SearchableViewMixin


class GlobalParameterView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[normalize-space(.)='Global Parameters']")

    @property
    def is_displayed(self):
        return self.title.is_displayed
