from widgetastic.widget import Text

from airgun.views.common import BaseLoggedInView, SearchableViewMixinPF4


class AboutView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[normalize-space(.)='About']")

    @property
    def is_displayed(self):
        return self.title.is_displayed
