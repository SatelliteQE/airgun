from widgetastic.widget import Text

from airgun.views.common import BaseLoggedInView, SearchableViewMixinPF4


class GlobalParameterView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[normalize-space(.)='Global Parameters']")

    @property
    def is_displayed(self):
        return self.title.is_displayed
