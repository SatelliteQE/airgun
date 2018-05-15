from wait_for import wait_for

from widgetastic.widget import (
    Checkbox,
    ConditionalSwitchableView,
    Select,
    Text,
    TextInput,
    View,
)

from airgun.views.common import (
    BaseLoggedInView,
    SatTab,
    SearchableViewMixin,
)
from airgun.widgets import (
    ActionsDropdown,
    ConfirmationDialog,
    EditableEntry,
    EditableEntrySelect,
    ReadOnlyEntry,
    SatSelect,
    SatTable,
    Search,
)


class CreateDiscoveredRepos(View):
    """View which represent Discovered Repository section in Repository
    Discovery procedure.
    """
    searchbox = Search()
    table = SatTable(
        locator=".//table",
        column_widgets={
            0: Checkbox(locator=".//input[@ng-change='itemSelected(urlRow)']")}
    )
    create_action = Text("//button[contains(., 'Create Selected')]")

    def search(self, value):
        self.searchbox.search(value)

    def fill(self, values):
        if not isinstance(values, list):
            values = list((values,))
        for value in values:
            self.table.row(discovered_repository__contains=value)[0].fill(True)
            self.create_action.click()

    def read(self):
        return self.table.read()


class ProductsTableView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h2[contains(., 'Products')]")
    new = Text("//button[contains(@href, '/products/new')]")
    edit = Text(
        "//td/a[contains(@ui-sref, 'product.repositories') and "
        "contains(@href, 'products')]"
    )
    repo_discovery = Text("//button[contains(.,'Repo Discovery')]")
    actions = ActionsDropdown("//div[contains(@class, 'btn-group')]")
    dialog = ConfirmationDialog()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class ProductCreateView(BaseLoggedInView):
    name = TextInput(id='name')
    label = TextInput(id='label')
    gpg_key = Select(id='gpg_key_id')
    ssl_ca_cert = Select(id='ssl_ca_cert_id')
    ssl_client_cert = Select(id='ssl_client_cert_id')
    ssl_client_key = Select(id='ssl_client_key_id')
    sync_plan = Select(id='sync_plan_id')
    description = TextInput(id='description')
    submit = Text("//button[contains(@ng-click, 'handleSave')]")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None


class ProductEditView(BaseLoggedInView):
    return_to_all = Text("//a[text()='Products']")
    actions = ActionsDropdown("//div[contains(@class, 'btn-group')]")
    dialog = ConfirmationDialog()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.return_to_all, exception=False) is not None

    @View.nested
    class details(SatTab):
        name = EditableEntry(name='Name')
        label = ReadOnlyEntry(name='Label')
        gpg_key = EditableEntrySelect(name='GPG Key')
        ssl_ca_cert = EditableEntrySelect(name='SSL CA Cert')
        ssl_client_cert = EditableEntrySelect(name='SSL Client Cert')
        ssl_client_key = EditableEntrySelect(name='SSL Client Key')
        description = EditableEntry(name='Description')
        repos_count = ReadOnlyEntry(name='Number of Repositories')
        tasks_count = ReadOnlyEntry(name='Active Tasks')
        sync_plan = EditableEntrySelect(name='Sync Plan')


class ProductRepoDiscoveryView(BaseLoggedInView, SearchableViewMixin):
    repo_type = Select(locator="//select[@ng-model='discovery.contentType']")
    url = TextInput(id='urlToDiscover')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.url, exception=False) is not None

    @View.nested
    class discovered_repos(View):
        discover_action = Text("//button[@type='submit']")
        cancel_discovery = Text("//button[@ng-click='cancelDiscovery()']")
        repos = CreateDiscoveredRepos()

        def before_fill(self, values=None):
            self.discover_action.click()
            wait_for(
                lambda: self.cancel_discovery.is_displayed is False,
                timeout=300,
                delay=1,
                logger=self.logger
            )

    @View.nested
    class create_repo(View):
        product_type = SatSelect(
            locator="//select[@ng-model='createRepoChoices.newProduct']")
        product_content = ConditionalSwitchableView(reference='product_type')

        @product_content.register('Existing Product')
        class ExistingProductForm(View):
            product_name = Select(
                locator="//select[@ng-model="
                        "'createRepoChoices.existingProductId']"
            )

        @product_content.register('New Product')
        class NewProductForm(View):
            product_name = TextInput(id='productName')
            label = TextInput(id='productLabel')
            gpg_key = Select(
                locator="//select[contains(@ng-model,"
                        " 'content_credential_id')]"
            )

        serve_via_http = Checkbox(id='unprotected')
        verify_ssl = Checkbox(id='verify_ssl')
        run_procedure = Text(
            "//button[contains(., 'Run Repository Creation')]")
        create_repos_table = SatTable('//table')

        def wait_repo_created(self):
            wait_for(
                lambda: self.create_repos_table.row(
                    create_status__contains='Repository created'
                ).is_displayed is True,
                timeout=300,
                delay=1,
                logger=self.logger
            )
