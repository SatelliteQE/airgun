from widgetastic.widget import (
    Checkbox,
    FileInput,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SearchableViewMixin, SatTab
from airgun.widgets import (
    DeleteSubscriptionConfirmationDialog,
    SatTable,
    SatSubscriptionsViewTable,
    ProgressBar
)


class SubscriptionListView(BaseLoggedInView, SearchableViewMixin):
    """List of all subscriptions."""
    table = SatSubscriptionsViewTable(
        locator='//*[@id="subscriptions-table"]//table',
        column_widgets={
            'Select all rows': Checkbox(locator=".//input[@type='checkbox']"),
            'Name': Text(".//a"),
        }
    )
    add_button = Text("//a[@href='subscriptions/add']")
    manage_manifest_button = Text("//button[text()='Manage Manifest']")
    export_csv_button = Text("//button[text()='Export CSV']")
    delete_button = Text("//button[text()='Delete']")
    progressbar = ProgressBar('//div[contains(@class, "progress-bar-striped")]')
    confirm_deletion = DeleteSubscriptionConfirmationDialog()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            'div#subscriptions-table', timeout=10, exception=False) is not None


class ManageManifestView(BaseLoggedInView):
    _locator = '//h4[@class="modal-title"][text()="Manage Manifest"]'
    ROOT = _locator + '/ancestor::div[@class="modal-content"]'
    close_button = Text(".//button[text()='Close']")

    @View.nested
    class manifest(SatTab):
        red_hat_cdn_url = TextInput(id='cdnUrl')
        manifest_file = FileInput(id='usmaFile')
        refresh_button = Text(".//button[text()='Refresh']")
        delete_button = Text(".//button[text()='Delete']")

    @View.nested
    class manifest_history(SatTab):
        TAB_NAME = "Manifest History"
        table = SatTable(
                locator="div#manifest-history-tabs table",
                column_widgets={
                    'Status': Text(),
                    'Message': Text(),
                    'Timestamp': Text()
                }
        )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self._locator, visible=True, exception=False) is not None


class DeleteManifestConfirmationView(BaseLoggedInView):
    _locator = '//h4[@class="modal-title"][text()="Confirm delete manifest"]'
    ROOT = _locator + '/ancestor::div[@class="modal-content"]'
    message = Text('.//div[@class="modal-body"]')
    delete_button = Text(".//button[text()='Delete']")
    cancel_button = Text(".//button[text()='Cancel']")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
                self._locator, visible=True, exception=False) is not None


class AddSubscriptionView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    table = SatTable(
            locator='.//table',
            column_widgets={
                'Subscription Name': Text('.//a'),
                'Quantity to Allocate': TextInput(locator='.//input'),
            }
    )
    submit_button = Text("//button[text()='Submit']")
    cancel_button = Text("//button[text()='Cancel']")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
                self.table, visible=True, exception=False) is not None


class SubscriptionDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    @View.nested
    class details(SatTab):
        provided_products = Text("//h2[text()='Provided Products']/following::ul")

    @View.nested
    class enabled_products(SatTab):
        TAB_NAME = "Enabled Products"

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
                self.breadcrumb, visible=True, exception=False) is not None
