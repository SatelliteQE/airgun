from wait_for import wait_for
from widgetastic.widget import Checkbox
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly4 import Button
from widgetastic_patternfly4 import Pagination
from widgetastic_patternfly4.ouia import Modal
from widgetastic_patternfly4.ouia import PatternflyTable

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SearchableViewMixin
from airgun.widgets import InventoryBootstrapSwitch


class CloudTokenView(BaseLoggedInView):
    """RH Cloud Insights Landing page for adding RH Cloud Token."""

    rhcloud_token = TextInput(locator='//input[contains(@aria-label, "input-cloud-token")]')
    save_token = Button('Save setting and sync recommendations')

    @property
    def is_displayed(self):
        return self.rhcloud_token.wait_displayed()


class RemediationView(Modal):
    """ Remediation window view"""

    remediate = Button('Remediate')
    cancel = Button('Cancel')
    table = PatternflyTable(
        component_id='OUIA-Generated-Table-2',
        column_widgets={
            'Hostname': Text('./a'),
            'Recommendation': Text('./a'),
            'Resolution': Text('.//a'),
            'Reboot Required': Text('.//a'),
        },
    )

    @property
    def is_displayed(self):
        return self.title.wait_displayed()


class CloudInsightsView(BaseLoggedInView, SearchableViewMixin):
    """Main RH Cloud Insights view."""

    title = Text('//h1[text()="Red Hat Insights"]')
    insights_sync_switcher = InventoryBootstrapSwitch(class_name='insights_sync_switcher')
    start_hits_sync = Button('Start recommendations sync')
    remediate = Button('Remediate')
    select_all = Checkbox(locator='.//input[@aria-label="Select all rows"]')
    table = PatternflyTable(
        component_id='OUIA-Generated-Table-2',
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            'Hostname': Text('.//a'),
            'Recommendation': Text('.//a'),
            'Total Risk': Text('.//a'),
            'Playbook': Text('.//a'),
        },
    )
    select_all_hits = Button('Select recommendations from all pages')
    clear_hits_selection = Button('Clear Selection')
    pagination = Pagination()
    remediation_window = View.nested(RemediationView)

    @property
    def is_displayed(self):
        return self.title.wait_displayed()

    def search(self, query):
        """Perform search using searchbox on the page and return table
        contents.

        :param str query: search query to type into search field. E.g. ``foo``
            or ``name = "bar"``.
        :return: list of dicts representing table rows
        :rtype: list
        """
        if not hasattr(self.__class__, 'table'):
            raise AttributeError(
                f'Class {self.__class__.__name__} does not have attribute "table". '
                'SearchableViewMixin only works with views, which have table for results. '
                'Please define table or use custom search implementation instead'
            )
        self.searchbox.search(query)
        wait_for(
            lambda: self.table.is_displayed is True,
            handle_exception=True,
            timeout=20,
            delay=1,
            logger=self.logger,
        )
        return self.table.read()
