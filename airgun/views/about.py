from widgetastic.widget import Text

from airgun.views.common import BaseLoggedInView, SearchableViewMixin


class AboutView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[normalize-space(.)='About']")

    @property
    def is_displayed(self):
        return self.title.is_displayed
