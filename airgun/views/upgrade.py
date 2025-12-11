from widgetastic.widget import Text

from airgun.views.common import BaseLoggedInView


class UpgradeView(BaseLoggedInView):
    title = Text("//h1[normalize-space(.)='Satellite upgrade']")
    new = Text("//a[contains(@href, 'documentation')]")

    @property
    def is_displayed(self):
        return self.title.is_displayed
