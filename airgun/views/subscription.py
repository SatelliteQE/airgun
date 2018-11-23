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
from airgun.views.common import BaseLoggedInView, SatTab, SearchableViewMixin
from airgun.widgets import (
    ConfirmationDialog,
    ItemsListReadOnly,
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
        return (self.browser.text(self.ROOT)
                != 'No products are enabled.')

    def read(self):
        result = wait_for(lambda: self.has_items,
                          timeout=5,
                          silent_failure=True)
        if not result:
            return []
        return [elem.text for elem in self.browser.elements(self.ITEMS)]

    def fill(self, value):
        raise ReadOnlyWidgetError('Widget is read only, fill is prohibited')


class SubscriptionListView(BaseLoggedInView, SubscriptionSearchableViewMixin):
    """List of all subscriptions."""
    table = SatSubscriptionsViewTable(
        locator='//div[@id="subscriptions-table"]//table',
        column_widgets={
            'Select all rows': Checkbox(locator=".//input[@type='checkbox']"),
            'Name': Text("./a"),
        }
    )
    add_button = Button(href='subscriptions/add')
    manage_manifest_button = Button('Manage Manifest')
    export_csv_button = Button('Export CSV')
    delete_button = Button('Delete')
    progressbar = ProgressBar('//div[contains(@class,"progress-bar-striped")]')
    confirm_deletion = DeleteSubscriptionConfirmationDialog()
    # In pre_navigate we wait for element with class `fade` to be not
    # visible; we need to first define it here
    fake_fade_widget = Text(".//div[contains(@class, 'fade')]")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            'div#subscriptions-table', timeout=10, exception=False) is not None

    def search(self, query):
        """Customized search to make sure that the table spinner is hidden, after search"""
        # the search box is always, but in case of no manifest subscription the welcome message is
        # always displayed.
        if self.welcome_message.is_displayed:
            return None
        self.searchbox.search(query)
        self.browser.plugin.ensure_page_safe(wait_for_spinner=True)
        return self.table.read()


class ManageManifestView(BaseLoggedInView):
    ROOT = ('//div[@role="dialog" and @tabindex]'
            '[div//h4[text()="Manage Manifest"]]')
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
        return (self.browser.wait_for_element(
                self.close_button, visible=True, exception=False) is not None
                and 'in' in self.browser.classes(self))

    def wait_animation_end(self):
        wait_for(
                lambda: 'in' in self.browser.classes(self),
                handle_exception=True, logger=self.logger, timeout=10
        )


class DeleteManifestConfirmationView(BaseLoggedInView):
    ROOT = ('//div[@role="dialog" and @tabindex]'
            '[div//h4[text()="Confirm delete manifest"]]')
    message = Text('.//div[@class="modal-body"]')
    delete_button = Button('Delete')
    cancel_button = Button('Cancel')

    @property
    def is_displayed(self):
        return (self.browser.wait_for_element(
                self.delete_button, visible=True, exception=False) is not None
                and 'in' in self.browser.classes(self))

    def wait_animation_end(self):
        wait_for(
                lambda: 'in' in self.browser.classes(self),
                handle_exception=True, logger=self.logger, timeout=10
        )


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

        associations = SatTable(
            locator=".//div[h2[text()='Associations']]/table",
            column_widgets={
                'Quantity': Text('.//a'),
            }
        )

        provided_products = ItemsListReadOnly(
                (".//h2[text()='Provided Products']/following::ul"))

    @View.nested
    class product_content(SatTab):
        TAB_NAME = "Product Content"

        product_content_list = ProductContentItemsList(".")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
                self.breadcrumb, visible=True, exception=False) is not None
