from wait_for import wait_for
from widgetastic.widget import (
    Checkbox,
    FileInput,
    GenericLocatorWidget,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb, Button

from airgun.exceptions import ReadOnlyWidgetError
from airgun.views.common import BaseLoggedInView, PF5ModalViewMixin, SatTab, SearchableViewMixin
from airgun.widgets import (
    ConfirmationDialog,
    ItemsListReadOnly,
    ProgressBar,
    SatTable,
)


class DeleteSubscriptionConfirmationDialog(ConfirmationDialog):
    confirm_dialog = Button('Delete')
    cancel_dialog = Button('Cancel')


class SatSubscriptionsViewTable(SatTable):
    """Table used on Red Hat Subscriptions page. It's mostly the same as
    normal table, but when search returns no results, it does display single
    row with message.
    Not to be confused with SatSubscriptionsTable, which is not used on
    that page.
    Note: When there are no subscriptions at all, Katello renders an EmptyState
    component instead of a table, so we need to check if the table exists first.
    """

    @property
    def is_displayed(self):
        """Check if the table element exists on the page."""
        return self.browser.is_element_present(self.locator)

    def wait_displayed(self, timeout=10):
        """Explicitly wait for the table to be displayed."""
        return self.browser.wait_for_element(self.locator, timeout=timeout, exception=False)

    @property
    def has_rows(self):
        return (
            self.is_displayed
            and self.tbody_row.read() != 'No subscriptions match your search criteria.'
        )


class ProductContentItemsList(GenericLocatorWidget):
    """Models list of enabled products (Subscriptions -> any ->
    Enabled products)
    Main reason is that page is constructed when tab is activated. There is
    no HTTP request, but delay is visible nevertheless - and during that time,
    message about no enabled product can be seen. We have to wait for a short
    while before we can be sure that there really are no products.
    """

    ITEMS = ".//div[contains(@class, 'list-group-item-heading')]"

    @property
    def has_items(self):
        return self.browser.text(self.ROOT) != 'No products are enabled.'

    def read(self):
        result = wait_for(lambda: self.has_items, timeout=5, silent_failure=True)
        if not result:
            return []
        return [elem.text for elem in self.browser.elements(self.ITEMS)]

    def fill(self, value):
        raise ReadOnlyWidgetError('Widget is read only, fill is prohibited')


class SubscriptionColumnsFilter(GenericLocatorWidget):
    """This is the list of interaction items for when opening up the selectable customizable
    checkboxes"""

    ITEMS_LOCATOR = "//div[@id='subscriptionTableTooltip']//li/span"
    CHECKBOX_LOCATOR = "//div[@id='subscriptionTableTooltip']//li/span[.='{}']/preceding::input[1]"

    @property
    def is_open(self):
        return 'tooltip-open' in self.browser.classes(self)

    def open(self):
        if not self.is_open:
            self.click()

    def close(self):
        if self.is_open:
            self.click()

    def checkboxes(self):
        labels = [line.text for line in self.browser.elements(self.ITEMS_LOCATOR)]
        return {
            label: Checkbox(self, locator=self.CHECKBOX_LOCATOR.format(label)) for label in labels
        }

    def read(self):
        """Read values of checkboxes"""
        self.open()
        values = {name: checkbox.read() for name, checkbox in self.checkboxes.items()}
        self.close()
        return values

    def fill(self, values):
        """Check or uncheck one of the checkboxes"""
        self.open()
        checkboxes = self.checkboxes()
        for name, value in values.items():
            checkboxes[name].fill(value)
        self.close()


class SubscriptionListView(BaseLoggedInView, SearchableViewMixin):
    """List of all subscriptions."""

    table = SatSubscriptionsViewTable(
        locator='//div[@id="subscriptions-table"]//table',
        column_widgets={
            'Select all rows': Checkbox(locator=".//input[@type='checkbox']"),
            'Name': Text('./a'),
        },
    )

    add_button = Button(href='subscriptions/add')
    manage_manifest_button = Button('Manage Manifest')
    import_manifest_button = Button('Import a Manifest')
    add_subscriptions_button = Button('Add subscriptions')
    export_csv_button = Button('Export CSV')
    delete_button = Button('Delete')
    progressbar = ProgressBar('//div[contains(@class,"progress-bar-striped")]')
    confirm_deletion = DeleteSubscriptionConfirmationDialog()
    columns_filter_checkboxes = SubscriptionColumnsFilter(
        ".//form[div[contains(@class, 'filter')]]/div/i"
    )

    @property
    def is_displayed(self):
        return (
            self.browser.wait_for_element('div#subscriptions-table', timeout=10, exception=False)
            is not None
        )

    def is_searchable(self):
        """Customized is_searchable"""
        # The search box is always displayed, but in case of no manifest subscription the
        # welcome message is always displayed and there is no table element.
        if self.welcome_message.is_displayed:
            return False
        return super().is_searchable()


class ManageManifestView(BaseLoggedInView, PF5ModalViewMixin):
    ROOT = '//div[@id="manageManifestModal"]'
    close_button = Button('Close')

    @View.nested
    class manifest(SatTab):
        alert_message = Text('.//div[contains(@class, "pf-v5-c-alert")]')
        expire_header = Text('//div[@id="manifest-history-tabs-pane-1"]/div/div/h4')
        expire_message = Text(
            '//div[@id="manifest-history-tabs-pane-1"]/div/div/h4//following-sibling::div'
        )
        expire_date = Text(
            '//div[@id="manifest-history-tabs-pane-1"]/div/hr//following-sibling::div[2]/div[2]'
        )
        red_hat_cdn_url = TextInput(id='cdnUrl')
        manifest_file = FileInput(id='usmaFile')
        refresh_button = Button('Refresh')
        delete_button = Button('Delete')

    @View.nested
    class manifest_history(SatTab):
        TAB_NAME = 'Manifest History'
        table = SatTable(
            locator='//div[@id="manifest-history-tabs"]//table',
            column_widgets={'Status': Text(), 'Message': Text(), 'Timestamp': Text()},
        )


class DeleteManifestConfirmationView(BaseLoggedInView, PF5ModalViewMixin):
    ROOT = '//div[@id="deleteManifestModal"]'
    message = Text('.//div[contains(@class, "pf-v5-c-modal-box__body")]')
    delete_button = Button('Delete')
    cancel_button = Button('Cancel')


class AddSubscriptionView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    table = SatTable(
        locator='.//table',
        column_widgets={
            'Subscription Name': Text('.//a'),
            'Quantity to Allocate': TextInput(locator='.//input'),
        },
    )
    submit_button = Button('Submit')
    cancel_button = Button('Cancel')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.table, visible=True, exception=False) is not None


class SubscriptionDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    @View.nested
    class details(SatTab):
        associations = SatTable(
            locator=".//div[h2[normalize-space(.)='Associations']]/table",
            column_widgets={
                'Quantity': Text('.//a'),
            },
        )

        provided_products = ItemsListReadOnly(
            ".//h2[normalize-space(.)='Provided Products']/following::ul"
        )

    @View.nested
    class product_content(SatTab):
        TAB_NAME = 'Product Content'

        product_content_list = ProductContentItemsList('.')

    @property
    def is_displayed(self):
        return (
            self.browser.wait_for_element(self.breadcrumb, visible=True, exception=False)
            is not None
        )
