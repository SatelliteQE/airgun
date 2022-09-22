from widgetastic.widget import Checkbox
from widgetastic.widget import ConditionalSwitchableView
from widgetastic.widget import FileInput
from widgetastic.widget import Select
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SearchableViewMixin
from airgun.widgets import ActionsDropdown
from airgun.widgets import ConfirmationDialog
from airgun.widgets import EditableEntry
from airgun.widgets import EditableEntryCheckbox
from airgun.widgets import EditableEntrySelect
from airgun.widgets import ReadOnlyEntry
from airgun.widgets import SatTable
from airgun.widgets import SatTableWithUnevenStructure


class RepositoriesView(BaseLoggedInView, SearchableViewMixin):
    breadcrumb = BreadCrumb()
    new = Text("//button[contains(@href, '/repositories/new')]")
    sync = Text("//button[contains(@ng-click, 'syncSelectedRepositories')]")
    delete = Text("//button[contains(@ng-show, 'canRemoveRepositories')]")
    dialog = ConfirmationDialog()
    table = SatTable(
        locator=".//table",
        column_widgets={
            0: Checkbox(locator=".//input[@ng-change='itemSelected(repository)']"),
            'Name': Text("./a[contains(@ui-sref, 'product.repository.info')]"),
        },
    )

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
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
        auth_token = TextInput(id='ansible_collection_auth_token')
        mirroring_policy = Select(id='mirroring_policy')
        include_tags = TextInput(id='include_tags')
        exclude_tags = TextInput(id='exclude_tags')
        http_proxy_policy = Select(id="http_proxy_policy")
        proxy_policy = ConditionalSwitchableView(reference='http_proxy_policy')
        ssl_ca_cert = Select(id='ssl_ca_cert_id')
        ssl_client_cert = Select(id='ssl_client_cert_id')
        ssl_client_key = Select(id='ssl_client_key_id')

        @proxy_policy.register('Use specific HTTP Proxy')
        class SpecificHttpProxy(View):
            http_proxy = Select(id="http_proxy")

    @repo_content.register('file')
    class FileRepository(View):
        upstream_url = TextInput(id='url')
        verify_ssl = Checkbox(id='verify_ssl_on_sync')
        upstream_username = TextInput(id='upstream_username')
        upstream_password = TextInput(id='upstream_password')
        auth_token = TextInput(id='ansible_collection_auth_token')
        mirroring_policy = Select(id='mirroring_policy')
        publish_via_http = Checkbox(id='unprotected')
        http_proxy_policy = Select(id="http_proxy_policy")
        proxy_policy = ConditionalSwitchableView(reference='http_proxy_policy')
        ssl_ca_cert = Select(id='ssl_ca_cert_id')
        ssl_client_cert = Select(id='ssl_client_cert_id')
        ssl_client_key = Select(id='ssl_client_key_id')

        @proxy_policy.register('Use specific HTTP Proxy')
        class SpecificHttpProxy(View):
            http_proxy = Select(id="http_proxy")

    @repo_content.register('ostree')
    class OstreeRepository(View):
        upstream_url = TextInput(id='url')
        upstream_sync_policy = Select(id='ostree_upstream_sync_policy')
        sync_policy_custom = TextInput(id='ostree_upstream_sync_depth')
        verify_ssl = Checkbox(id='verify_ssl_on_sync')
        upstream_username = TextInput(id='upstream_username')
        upstream_password = TextInput(id='upstream_password')
        http_proxy_policy = Select(id="http_proxy_policy")
        proxy_policy = ConditionalSwitchableView(reference='http_proxy_policy')

        @proxy_policy.register('Use specific HTTP Proxy')
        class SpecificHttpProxy(View):
            http_proxy = Select(id="http_proxy")

    @repo_content.register('yum')
    class YumRepository(View):
        arch_restrict = Select(id='architecture_restricted')
        os_restrict = Select(id='os_versions')
        upstream_url = TextInput(id='url')
        ignore_srpms = Checkbox(id='ignore_srpms')
        verify_ssl = Checkbox(id='verify_ssl_on_sync')
        upstream_username = TextInput(id='upstream_username')
        upstream_password = TextInput(id='upstream_password')
        auth_token = TextInput(id='ansible_collection_auth_token')
        download_policy = Select(id='download_policy')
        mirroring_policy = Select(id='mirroring_policy')
        retain_package_versions = TextInput(id='retain_package_versions_count')
        checksum_type = Select(id='checksum_type')
        publish_via_http = Checkbox(id='unprotected')
        unprotected = Checkbox(id='unprotected')
        gpg_key = Select(id='gpg_key_id')
        ssl_ca_cert = Select(id='ssl_ca_cert_id')
        ssl_client_cert = Select(id='ssl_client_cert_id')
        ssl_client_key = Select(id='ssl_client_key_id')
        http_proxy_policy = Select(id="http_proxy_policy")
        proxy_policy = ConditionalSwitchableView(reference='http_proxy_policy')

        @proxy_policy.register('Use specific HTTP Proxy')
        class SpecificHttpProxy(View):
            http_proxy = Select(id="http_proxy")

    @repo_content.register('ansible collection')
    class AnsibleCollectionRepository(View):
        arch_restrict = Select(id='architecture_restricted')
        upstream_url = TextInput(id='url')
        requirements = TextInput(id='ansible_collection_requirements')
        requirements_btn = FileInput(id='requirementFile')
        auth_url = TextInput(id='ansible_collection_auth_url')
        auth_token = TextInput(id='ansible_collection_auth_token')
        verify_ssl = Checkbox(id='verify_ssl_on_sync')
        upstream_username = TextInput(id='upstream_username')
        upstream_password = TextInput(id='upstream_password')
        mirroring_policy = Select(id='mirroring_policy')
        http_proxy_policy = Select(id="http_proxy_policy")
        proxy_policy = ConditionalSwitchableView(reference='http_proxy_policy')
        ssl_ca_cert = Select(id='ssl_ca_cert_id')
        ssl_client_cert = Select(id='ssl_client_cert_id')
        ssl_client_key = Select(id='ssl_client_key_id')

        @proxy_policy.register('Use specific HTTP Proxy')
        class SpecificHttpProxy(View):
            http_proxy = Select(id="http_proxy")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Products'
            and self.breadcrumb.locations[2] == 'Repositories'
            and self.breadcrumb.read() == 'New Repository'
        )


class AuthorizationEntry(EditableEntry):

    clear_button = Text(".//span[contains(@ng-hide, 'editMode')]/i[@ng-show='deletable']")

    @View.nested
    class edit_field(View):
        username = TextInput(id='upstream_username')
        password = TextInput(id='upstream_password')

    def fill(self, value):
        """Handle the clear functionality, if bool(value) is False clear the credentials."""
        if not value and self.clear_button.is_displayed:
            self.clear_button.click()
            return
        return super().fill(value)


class RepositoryEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    actions = ActionsDropdown("//div[contains(@class, 'btn-group')]")
    dialog = ConfirmationDialog()
    name = EditableEntry(name='Name')
    label = ReadOnlyEntry(name='Label')
    repo_type = ReadOnlyEntry(name='Type')
    repo_content = ConditionalSwitchableView(reference='repo_type')
    content_counts = SatTableWithUnevenStructure(
        locator='.//table[//th[normalize-space(.)="Content Type"]]', column_locator='./*'
    )

    @repo_content.register('docker')
    class DockerRepository(View):
        registry_url = EditableEntry(name='Registry URL')
        upstream_repo_name = EditableEntry(name='Upstream Repository')
        repo_name = ReadOnlyEntry(name='Name')
        verify_ssl = EditableEntryCheckbox(name='Verify SSL')
        upstream_authorization = AuthorizationEntry(name='Upstream Authorization')
        http_proxy_policy = EditableEntrySelect(name='HTTP Proxy')
        proxy_policy = ConditionalSwitchableView(reference='http_proxy_policy')
        mirroring_policy = EditableEntrySelect(name='Mirroring Policy')
        include_tags = EditableEntry(name='Include Tags')
        exclude_tags = EditableEntry(name='Exclude Tags')

        @proxy_policy.register(True, default=True)
        class NoSpecificHttpProxy(View):
            pass

    @repo_content.register('yum')
    class YumRepository(View):
        arch_restrict = EditableEntrySelect(name='Restrict to architecture')
        os_restrict = EditableEntrySelect(name='Restrict to OS version')
        verify_ssl = EditableEntryCheckbox(name='Verify SSL')
        upstream_url = EditableEntry(name='Upstream URL')
        upstream_authorization = AuthorizationEntry(name='Upstream Authorization')
        metadata_type = EditableEntrySelect(name='Yum Metadata Checksum')
        retain_package_versions = EditableEntry(name='Retain package versions')
        http_proxy_policy = EditableEntrySelect(name='HTTP Proxy')
        ignore_srpms = EditableEntryCheckbox(name='Ignore SRPMs')
        unprotected = EditableEntryCheckbox(name='Unprotected')
        gpg_key = EditableEntrySelect(name='GPG Key')
        download_policy = EditableEntrySelect(name='Download Policy')
        mirroring_policy = EditableEntrySelect(name='Mirroring Policy')
        upload_content = FileInput(name='content[]')
        upload = Text("//button[contains(., 'Upload')]")
        proxy_policy = ConditionalSwitchableView(reference='http_proxy_policy')

        @proxy_policy.register(True, default=True)
        class NoSpecificHttpProxy(View):
            pass

    @repo_content.register('ansible collection')
    class AnsibleCollectionRepository(View):
        arch_restrict = EditableEntrySelect(name='Restrict to architecture')
        upstream_url = EditableEntry(name='Upstream URL')
        requirements = EditableEntry(name='Requirements')
        verify_ssl = EditableEntryCheckbox(name='Verify SSL')
        upstream_authorization = AuthorizationEntry(name='Upstream Authorization')
        upload_content = FileInput(name='content[]')
        upload = Text("//button[contains(., 'Upload')]")
        http_proxy_policy = EditableEntrySelect(name='HTTP Proxy')
        proxy_policy = ConditionalSwitchableView(reference='http_proxy_policy')
        mirroring_policy = EditableEntrySelect(name='Mirroring Policy')

        @proxy_policy.register(True, default=True)
        class NoSpecificHttpProxy(View):
            pass

    @repo_content.register('ostree')
    class OstreeRepository(View):
        upstream_url = EditableEntry(name='Upstream URL')
        verify_ssl = EditableEntryCheckbox(name='Verify SSL')
        upstream_authorization = AuthorizationEntry(name='Upstream Authorization')
        published_at = ReadOnlyEntry(name='Published At')
        http_proxy_policy = EditableEntrySelect(name='HTTP Proxy')
        proxy_policy = ConditionalSwitchableView(reference='http_proxy_policy')

        @proxy_policy.register(True, default=True)
        class NoSpecificHttpProxy(View):
            pass

    @repo_content.register('file')
    class FileRepository(View):
        upstream_url = EditableEntry(name='Upstream URL')
        verify_ssl = EditableEntryCheckbox(name='Verify SSL')
        upstream_authorization = AuthorizationEntry(name='Upstream Authorization')
        unprotected = EditableEntryCheckbox(name='Unprotected')
        mirroring_policy = EditableEntrySelect(name='Mirroring Policy')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Products'
            # repositories do not have tabs, so if we are deep inside some
            # specific repository (e.g. in repository packages) - there's no
            # turn back, so we can't treat any level deeper than repository
            # details like details' sub-tab
            and self.breadcrumb.locations[-2] == 'Repositories'
            and self.breadcrumb.read() != 'New Repository'
        )


class RepositoryPackagesView(BaseLoggedInView, SearchableViewMixin):
    breadcrumb = BreadCrumb()
    dialog = ConfirmationDialog()
    table = SatTable(
        locator=".//table",
        column_widgets={
            0: Checkbox(locator=".//input[@ng-change='itemSelected(package)']"),
        },
    )
    select_all = Checkbox(locator=".//input[@type='checkbox'][@ng-change='allSelected()']")
    items_per_page = Select(locator=".//select[@ng-model='table.params.per_page']")
    total_packages = Text("//span[@class='pagination-pf-items-total ng-binding']")
    remove_packages = Text(".//button[@ng-click='openModal()']")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Products'
            and self.breadcrumb.locations[2] == 'Repositories'
            and self.breadcrumb.read() == 'Packages'
        )
