from widgetastic.widget import Checkbox
from widgetastic.widget import Table
from widgetastic.widget import Text

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SearchableViewMixin
from airgun.widgets import ActionsDropdown


class OSCAPReportsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Compliance Reports']")
    delete_reports = Text("//div[@id='submit_multiple']")
    select_all = Checkbox(locator="//input[@id='check_all']")
    table = Table(
        './/table',
        column_widgets={
            0: Checkbox(
                locator=".//input[@class='host_select_boxes']"),
            'Host': Text('./a'),
            'Reported At': Text('./a'),
            'Policy': Text('./a'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class DeletereportsDialog(BaseLoggedInView):
    """Class for Oscap reports Delete Action."""
    title = Text(
        "//h4[text()='Delete reports - The following compliance reports are about to be changed']")
    table = Table("//div[@class='modal-body']//table")
    submit = Text('//button[@onclick="tfm.hosts.table.submitModalForm()"]')
    cancel = Text("//a[text()='Cancel']")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None
