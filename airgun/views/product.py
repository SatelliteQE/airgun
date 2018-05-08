from widgetastic.widget import Select, Text, TextInput, View

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
)


class ProductsTableView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h2[contains(., 'Products')]")
    new = Text("//button[contains(@href, '/products/new')]")
    edit = Text(
        "//td/a[contains(@ui-sref, 'product.repositories') and "
        "contains(@href, 'products')]"
    )
    repo_discovery = Text("//button[contains(.,'Repo Discovery')]")
    actions = ActionsDropdown("//td//div[contains(@class, 'btn-group')]")
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
    class Details(SatTab):
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
