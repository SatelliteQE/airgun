from widgetastic.widget import Text, TextInput

from airgun.views.common import BaseLoggedInView


class AllRulesView(BaseLoggedInView):
    title = Text(".//h1[normalize-space(.)='Rules']")
    search = TextInput(locator=".//input[@placeholder='Search rules']")

    @property
    def is_displayed(self):
        return self.title.is_displayed and self.search.is_displayed
