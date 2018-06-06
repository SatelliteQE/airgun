from widgetastic.widget import (
    Checkbox,
    ConditionalSwitchableView,
    Select,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import (
    ActionsDropdown,
    ConfirmationDialog,
    EditableEntry,
    EditableEntryCheckbox,
    EditableEntrySelect,
    ReadOnlyEntry,
    SatTable,
)


class RepositoriesView(BaseLoggedInView, SearchableViewMixin):
    breadcrumb = BreadCrumb()
    new = Text("//button[contains(@href, '/repositories/new')]")
    sync = Text("//button[contains(@ng-click, 'syncSelectedRepositories')]")
    delete = Text("//button[contains(@ng-show, 'canRemoveRepositories')]")
    dialog = ConfirmationDialog()
    table = SatTable(
        locator=".//table",
        column_widgets={
            0: Checkbox(
                locator=".//input[@ng-change='itemSelected(repository)']"),
            'Name': Text("./a[contains(@ui-sref, 'product.repository.info')]"),
        }
    )

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Products'
                and self.breadcrumb.read() == 'Repositories'
        )


class RepositoryCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='name')
    label = TextInput(id='label')
    repo_type = Select(id='content_type')
    submit = Text("//button[contains(@ng-click, 'handleSave')]")
    repo_content = ConditionalSwitchableView(reference='repo_type')

    @repo_content.register('docker')
    class DockerRepository(View):
        upstream_url = TextInput(id='url')
        upstream_repo_name = TextInput(id='docker_upstream_name')
        verify_ssl = Checkbox(id='verify_ssl_on_sync')
        upstream_username = TextInput(id='upstream_username')
        upstream_password = TextInput(id='upstream_password')
        ignore_global_proxy = TextInput(id='ignore_global_proxy')

    @repo_content.register('file')
    class FileRepository(View):
        upstream_url = TextInput(id='url')
        verify_ssl = Checkbox(id='verify_ssl_on_sync')
        upstream_username = TextInput(id='upstream_username')
        upstream_password = TextInput(id='upstream_password')
        ignore_global_proxy = TextInput(id='ignore_global_proxy')
        publish_via_http = Checkbox(id='unprotected')

    @repo_content.register('ostree')
    class OstreeRepository(View):
        upstream_url = TextInput(id='url')
        upstream_sync_policy = Select(id='ostree_upstream_sync_policy')
        sync_policy_custom = TextInput(id='ostree_upstream_sync_depth')
        verify_ssl = Checkbox(id='verify_ssl_on_sync')
        upstream_username = TextInput(id='upstream_username')
        upstream_password = TextInput(id='upstream_password')
        ignore_global_proxy = TextInput(id='ignore_global_proxy')

    @repo_content.register('puppet')
    class PuppetRepository(View):
        upstream_url = TextInput(id='url')
        verify_ssl = Checkbox(id='verify_ssl_on_sync')
        upstream_username = TextInput(id='upstream_username')
        upstream_password = TextInput(id='upstream_password')
        mirror_on_sync = Checkbox(id='mirror_on_sync')
        ignore_global_proxy = TextInput(id='ignore_global_proxy')
        publish_via_http = Checkbox(id='unprotected')

    @repo_content.register('yum')
    class YumRepository(View):
        arch_restrict = Select(id='architecture_restricted')
        upstream_url = TextInput(id='url')
        verify_ssl = Checkbox(id='verify_ssl_on_sync')
        upstream_username = TextInput(id='upstream_username')
        upstream_password = TextInput(id='upstream_password')
        download_policy = Select(id='download_policy')
        mirror_on_sync = Checkbox(id='mirror_on_sync')
        ignore_global_proxy = TextInput(id='ignore_global_proxy')
        checksum_type = Select(id='checksum_type')
        publish_via_http = Checkbox(id='unprotected')
        gpg_key = Select(id='gpg_key_id')
        ssl_ca_cert = Select(id='ssl_ca_cert_id')
        ssl_client_cert = Select(id='ssl_client_cert_id')
        ssl_client_key = Select(id='ssl_client_key_id')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Products'
                and self.breadcrumb.read() == 'Repositories'
                and self.breadcrumb.read() == 'New Repository'
        )


class RepositoryEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    actions = ActionsDropdown("//div[contains(@class, 'btn-group')]")
    dialog = ConfirmationDialog()
    name = EditableEntry(name='Name')
    label = ReadOnlyEntry(name='Label')
    repo_type = ReadOnlyEntry(name='Type')
    repo_content = ConditionalSwitchableView(reference='repo_type')

    @repo_content.register('docker')
    class DockerRepository(View):
        registry_url = EditableEntry(name='Registry URL')
        upstream_repo_name = EditableEntry(name='Upstream Repository')
        repo_name = ReadOnlyEntry(name='Name')
        verify_ssl = EditableEntryCheckbox(name='Verify SSL')
        upstream_username = EditableEntry(name='Upstream Username')
        upstream_password = EditableEntry(name='Upstream Password')
        ignore_global_proxy = EditableEntryCheckbox(name='Ignore Global HTTP')
        publish_via_http = EditableEntryCheckbox(name='Publish via HTTP')

    @repo_content.register('yum')
    class YumRepository(View):
        arch_restrict = EditableEntrySelect(name='Restrict to architecture')
        upstream_repo_url = EditableEntry(name='Upstream URL')
        verify_ssl = EditableEntryCheckbox(name='Verify SSL')
        upstream_username = EditableEntry(name='Upstream Username')
        upstream_password = EditableEntry(name='Upstream Password')
        metadata_type = EditableEntrySelect(name='Yum Metadata Checksum')
        mirror_on_sync = EditableEntryCheckbox(name='Mirror on Sync')
        ignore_global_proxy = EditableEntryCheckbox(name='Ignore Global HTTP')
        publish_via_http = EditableEntryCheckbox(name='Publish via HTTP:')
        gpg_key = EditableEntrySelect(name='GPG Key')
        download_policy = EditableEntrySelect(name='Download Policy')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Products'
            and self.breadcrumb.read() == 'Repositories'
            and self.breadcrumb.read() != 'New Repository'
        )
