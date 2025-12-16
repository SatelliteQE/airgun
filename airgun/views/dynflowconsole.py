from widgetastic.widget import Text
from widgetastic_patternfly4 import Pagination as PF4Pagination

from airgun.views.common import BaseLoggedInView


class DynflowConsoleView(BaseLoggedInView):
    title = Text("//a[@class='navbar-brand']//img")
    output = Text("//div[@class='action']/pre[2]")

    pagination = PF4Pagination()

    @property
    def is_displayed(self):
        return self.title.is_displayed
