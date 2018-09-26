from selenium.common.exceptions import NoSuchElementException

from widgetastic.widget import (
    Checkbox,
    FileInput,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb, Button

from airgun.views.common import BaseLoggedInView, SatTab, SearchableViewMixin
from airgun.widgets import (
    ConfirmationDialog,
    ProgressBar,
    SatTable,
    Search,
)


# Search field and button on Subscriptions page uses different locators,
# so subclass it and use it in our custom SearchableViewMixin
class SubscriptionSearch(Search):
    search_field = TextInput(locator=(
        ".//input[starts-with(@id, 'downshift-')]"))
    search_button = Button('Search')


class SubscriptionSearchableViewMixin(SearchableViewMixin):
    searchbox = SubscriptionSearch()


class DeleteSubscriptionConfirmationDialog(ConfirmationDialog):
    confirm_dialog = Button('Delete')
    cancel_dialog = Button('Cancel')


class SatSubscriptionsViewTable(SatTable):
    """Table used on Red Hat Subscriptions page. It's mostly the same as
    normal table, but when search returns no results, it does display single
    row with message.
    Not to be confused with SatSubscriptionsTable, which is not used on
    that page
    """
    @property
    def has_rows(self):
        return (self.tbody_row.read()
                != "No subscriptions match your search criteria."
                )


class SubscriptionListView(BaseLoggedInView, SubscriptionSearchableViewMixin):
    """List of all subscriptions."""
    table = SatSubscriptionsViewTable(
        locator='//*[@id="subscriptions-table"]//table',
        column_widgets={
            'Select all rows': Checkbox(locator=".//input[@type='checkbox']"),
            'Name': Text(".//a"),
        }
    )
    add_button = Button(href='subscriptions/add')
    manage_manifest_button = Button('Manage Manifest')
    export_csv_button = Button('Export CSV')
    delete_button = Button('Delete')
    progressbar = ProgressBar('//div[contains(@class,"progress-bar-striped")]')
    confirm_deletion = DeleteSubscriptionConfirmationDialog()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            'div#subscriptions-table', timeout=10, exception=False) is not None


class ManageManifestView(BaseLoggedInView):
    ROOT = '//div[@class="modal-content"][div/h4[text()="Manage Manifest"]]'
    close_button = Button('Close')

    @View.nested
    class manifest(SatTab):
        red_hat_cdn_url = TextInput(id='cdnUrl')
        manifest_file = FileInput(id='usmaFile')
        refresh_button = Button('Refresh')
        delete_button = Button('Delete')

    @View.nested
    class manifest_history(SatTab):
        TAB_NAME = "Manifest History"
        table = SatTable(
                locator='//div[@id="manifest-history-tabs"]//table',
                column_widgets={
                    'Status': Text(),
                    'Message': Text(),
                    'Timestamp': Text()
                }
        )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.close_button, visible=True, exception=False) is not None


class DeleteManifestConfirmationView(BaseLoggedInView):
    ROOT = ('//div[@class="modal-content"]'
            '[div/h4[text()="Confirm delete manifest"]]')
    message = Text('.//div[@class="modal-body"]')
    delete_button = Button('Delete')
    cancel_button = Button('Cancel')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
                self.delete_button, visible=True, exception=False) is not None


class AddSubscriptionView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    table = SatTable(
            locator='.//table',
            column_widgets={
                'Subscription Name': Text('.//a'),
                'Quantity to Allocate': TextInput(locator='.//input'),
            }
    )
    submit_button = Button('Submit')
    cancel_button = Button('Cancel')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
                self.table, visible=True, exception=False) is not None


class SubscriptionDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    @View.nested
    class details(SatTab):

        @property
        def provided_products(self):
            return [elem.text
                    for elem
                    in self.browser.elements(
                        ("//h2[text()='Provided Products']"
                         "/following::ul/li"))]

    @View.nested
    class enabled_products(SatTab):
        TAB_NAME = "Enabled Products"

        @property
        def enabled_products_list(self):
            locator = ("//div[contains(@class, 'list-group')]"
                       "//div[contains(@class, 'list-group-item-heading')]"
                       )
            try:
                self.browser.wait_for_element(locator, visible=True)
            except NoSuchElementException:
                return []
            return [elem.text for elem in self.browser.elements(locator)]

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
                self.breadcrumb, visible=True, exception=False) is not None
