from widgetastic.widget import Text
from widgetastic.xpath import quote
from widgetastic_patternfly5 import (
    Alert as PF5Alert,
    Button as PF5Button,
    Menu as PF5Menu,
    Modal as PF5Modal,
    Pagination,
)
from widgetastic_patternfly5.ouia import (
    PatternflyTable as PF5OUIATable,
    Text as PF5OUIAText,
    TextInput as PF5OUIATextInput,
    Title as PF5OUIATitle,
)

from airgun.views.common import BaseLoggedInView, SearchableViewMixinPF4
from airgun.widgets import SearchInput


class FlatpakRemotesView(BaseLoggedInView, SearchableViewMixinPF4):
    """View for the Flatpak Remotes page"""

    title = Text("//h1[normalize-space(.)='Flatpak Remotes']")

    table_loading = Text("//h5[normalize-space(.)='Loading']")
    no_results = Text("//h5[normalize-space(.)='No Results']")

    create_new_btn = PF5Button('Create new')

    table = PF5OUIATable(
        component_id='flatpak-remotes-table',
        column_widgets={
            'Name': Text('./a[contains(@href, "flatpak_remotes")]'),
            'URL': Text('./a'),
            2: PF5Menu(locator='.//div[contains(@class, "pf-v5-c-menu")]'),
        },
    )
    pagination = Pagination()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.create_new_btn, exception=False) is not None


class FlatpakRemoteDetailsView(BaseLoggedInView, SearchableViewMixinPF4):
    """View for the Flatpak Remote details page"""

    title = PF5OUIATitle('flatpak-remote-title')
    url = PF5OUIAText('url-text-value')
    subtitle = PF5OUIATitle('flatpak-remote-subtitle')
    description = PF5OUIAText('flatpak-remote-description')

    table = PF5OUIATable(
        component_id='remote-repos-table',
        column_widgets={
            'Name': Text('./a'),
            'ID': Text('./a'),
            'Application name': Text('./a'),
            'Last mirrored': Text('./a'),
            'Mirror': PF5Button('Mirror'),
        },
    )
    pagination = Pagination("//div[@class = 'pf-v5-c-pagination pf-m-bottom tfm-pagination']")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class CreateFlatpakRemoteModal(PF5Modal):
    """View for the Create Flatpak Remote modal"""

    ROOT = './/div[@data-ouia-component-id="create-flatpak-modal"]'

    title = Text("//span[normalize-space(.)='Create Flatpak remote']")

    info_alert = PF5Alert(locator='.//div[@data-ouia-component-id="flatpak-remote-info-alert"]')
    add_rh_fr = PF5Button('Add Red Hat flatpak remote')

    name = PF5OUIATextInput('input_name')
    url = PF5OUIATextInput('input_url')
    username = PF5OUIATextInput('input_username')
    password = PF5OUIATextInput('input_password')

    create_btn = PF5Button('Create')
    cancel_btn = PF5Button('Cancel')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class EditFlatpakRemoteModal(PF5Modal):
    """View for the Edit Flatpak Remote modal"""

    ROOT = './/div[@data-ouia-component-id="edit-flatpak-modal"]'

    title = Text("//span[normalize-space(.)='Edit Flatpak remote']")

    name = PF5OUIATextInput('input_name')
    url = PF5OUIATextInput('input_url')
    username = PF5OUIATextInput('input_username')
    password = PF5OUIATextInput('input_password')

    update_btn = PF5Button('Update')
    cancel_btn = PF5Button('Cancel')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class MirrorFlatpakRemoteModal(PF5Modal, SearchableViewMixinPF4):
    """View for the Mirror Flatpak Remote modal"""

    ROOT = './/div[@data-ouia-component-id="mirror-repo-modal"]'

    title = Text("//span[normalize-space(.)='Mirror Repository']")

    searchbar = SearchInput(
        locator='.//input[contains(@class, "pf-v5-c-text-input-group__text-input")]'
    )

    dependency_alert = PF5Alert(locator='.//div[@data-ouia-component-id="dependency-alert"]')
    dependency_info = PF5OUIAText('dependency-info-text')

    mirror_btn = PF5Button('Mirror')
    cancel_btn = PF5Button('Cancel')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None

    def dependency_repo_names(self):
        """Return a list of dependency repository names from the alert."""
        if not self.dependency_alert.is_displayed:
            return []
        repo_nodes = self.browser.elements(
            './/div[@data-ouia-component-id="dependency-alert"]//label//strong'
        )
        return [self.browser.text(node) for node in repo_nodes]

    def select_dependency(self, repo_name):
        """Select a dependency checkbox by repository name."""
        label = self.browser.element(
            './/div[@data-ouia-component-id="dependency-alert"]//label['
            f'.//strong[normalize-space(.)={quote(repo_name)}]'
            ']'
        )
        checkbox_id = label.get_attribute('for')
        checkbox = self.browser.element(f'.//input[@id={quote(checkbox_id)}]')
        checkbox.click()


class FlatpakRemoteDeleteModal(PF5Modal):
    """Confirmation dialog for deleting Flatpak Remote"""

    ROOT = './/div[@data-ouia-component-id="flatpak-delete-modal"]'

    title = Text("//span[normalize-space(.)='Delete Flatpak remote?']")

    delete_btn = PF5Button('Delete')
    cancel_btn = PF5Button('Cancel')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None
