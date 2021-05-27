from widgetastic.widget import Table
from widgetastic.widget import Checkbox

from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly4 import Button
from widgetastic_patternfly4 import Pagination
from airgun.widgets import InventoryBootstrapSwitch

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SearchableViewMixin


class CloudInsightsView(BaseLoggedInView, SearchableViewMixin):
    """Main RH Cloud Inventory Upload view."""
    title = Text('//h1[text()="Red Hat Insights"]')
    rhcloud_token = TextInput(locator='//input[contains(@aria-label, "input-cloud-token")]')
    save_token = Button(locator='//button[text()="Save setting and sync recommendations"]')
    insights_sync_switcher = InventoryBootstrapSwitch(class_name='insights_sync_switcher')
    start_hits_sync = Button(locator='//button[text()="Start recommendations sync"]')
    # remediate = Button(locator='//button[text()="Remediate"]')
    select_all = Checkbox(locator='.//input[@aria-label="Select all rows"]')
    table = Table(
        './/table',
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            'Hostname': Text('.//a'),
            'Recommendation': Text('.//a'),
            'Total Risk': Text('.//a'),
            'Playbook': Text(".//a"),
        },
    )
    select_all_hits = Button(locator='//button[text()="Select recommendations from all pages"]')
    clear_hits_selection = Button(locator='//button[text()="Clear Selection"]')
    pagination = Pagination()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None
