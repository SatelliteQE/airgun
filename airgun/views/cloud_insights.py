from widgetastic.widget import Table
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly4 import Button

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SearchableViewMixin


class CloudInsightsView(BaseLoggedInView, SearchableViewMixin):
    title = Text('//h1[text()="Red Hat Insights"]')
    rhcloud_token = TextInput(locator='//input[contains(@aria-label, "input-cloud-token")]')
    save_token = Button(locator='//button[text()="Save setting and sync recommendations"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None