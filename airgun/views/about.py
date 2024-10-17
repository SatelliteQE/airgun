from widgetastic.widget import Text

from airgun.views.common import BaseLoggedInView, SearchableViewMixinPF4


class AboutView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[normalize-space(.)='About']")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None
