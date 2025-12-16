from widgetastic.exceptions import NoSuchElementException

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.flatpak import (
    CreateFlatpakRemoteModal,
    EditFlatpakRemoteModal,
    FlatpakRemoteDeleteModal,
    FlatpakRemoteDetailsView,
    FlatpakRemotesView,
    MirrorFlatpakRemoteModal,
)


class FlatpakRemotesEntity(BaseEntity):
    """Entity for Flatpak remotes."""

    endpoint_path = '/flatpak_remotes'

    def search(self, value):
        """Search for Flatpak remote in the table.

        :param str value: search query to type into search field.
        :return: list of table rows that match the search query
        :rtype: list
        """
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, widget_names=None):
        """Read all values for widgets in the view.

        :param list widget_names: list of widgets to read
        :return: dict of widget names and their values
        :rtype: dict
        """
        view = self.navigate_to(self, 'All')
        return view.read(widget_names=widget_names)

    def read_table(self):
        """Read the table of Flatpak remotes.

        :return: list of table rows
        :rtype: list
        """
        view = self.navigate_to(self, 'All')
        return view.table.read()

    def read_remote_details(self, name, repo_search=None):
        """
        Read details from the Flatpak remote details page

        Args:
            name (str): Name of the flatpak remote to be read
            repo_search (str, optional): Name of scanned remote repository to be searched
        """
        view = self.navigate_to(self, 'All')
        view.search(name)
        view.table.row(name=name)['Name'].widget.click()
        view = FlatpakRemoteDetailsView(self.browser)

        if repo_search:
            view.search(repo_search)
            self.browser.plugin.ensure_page_safe()
        return view.read()

    def create(self, values):
        """Create a Flatpak remote.

        :param dict values: values to create the remote with
        """
        view = self.navigate_to(self, 'All')
        view.create_new_btn.click()
        create_modal = CreateFlatpakRemoteModal(self.browser)

        create_modal.fill(values)
        create_modal.create_btn.click()
        view = FlatpakRemoteDetailsView(self.browser)
        view.wait_displayed(delay=3)

    def create_redhat_remote(self, values):
        """Create a Red Hat Flatpak remote using the info alert action.

        This method clicks the 'Add Red Hat flatpak remote' button from the
        info alert instead of manually filling the URL.

        :param dict values: values to create the remote with
        """
        view = self.navigate_to(self, 'All')
        view.create_new_btn.click()
        create_modal = CreateFlatpakRemoteModal(self.browser)

        create_modal.fill(values)

        if create_modal.info_alert.is_displayed:
            create_modal.add_rh_fr.click()
        else:
            raise ValueError('Red Hat Flatpak remote info alert is not displayed')

        create_modal.create_btn.click()
        view = FlatpakRemoteDetailsView(self.browser)
        view.wait_displayed(delay=3)

    def read_create_modal_alert(self):
        """Read the info alert from the Create Flatpak Remote modal.

        :return: dict with alert information or None if alert not displayed
        """
        view = self.navigate_to(self, 'All')
        view.create_new_btn.click()
        create_modal = CreateFlatpakRemoteModal(self.browser)

        if create_modal.info_alert.is_displayed:
            alert_info = {
                'title': create_modal.info_alert.title,
                'body': create_modal.info_alert.body,
            }
            create_modal.cancel_btn.click()
            return alert_info

        create_modal.cancel_btn.click()
        return None

    def edit(self, entity_name, values):
        """Edit a Flatpak remote.

        :param str entity_name: name of the remote to edit
        :param dict values: values to update the remote with
        """
        view = self.navigate_to(self, 'All')
        view.table.row(name=entity_name)[2].click()
        view.table.row(name=entity_name)[2].widget.item_select('Edit')
        edit_modal = EditFlatpakRemoteModal(self.browser)

        edit_modal.fill(values)
        edit_modal.update_btn.click()
        view = FlatpakRemoteDetailsView(self.browser)
        view.wait_displayed(delay=3)

    def delete(self, entity_name):
        """Delete a Flatpak remote.

        :param str entity_name: name of the remote to delete
        """
        view = self.navigate_to(self, 'All')
        view.table.row(name=entity_name)[2].click()
        view.table.row(name=entity_name)[2].widget.item_select('Delete')
        delete_modal = FlatpakRemoteDeleteModal(self.browser)

        delete_modal.delete_btn.click()

        view = FlatpakRemotesView(self.browser)
        view.wait_displayed(delay=3)

    def scan(self, entity_name):
        """Scan a Flatpak remote.

        :param str entity_name: name of the remote to scan
        """
        view = self.navigate_to(self, 'All')
        view.table.row(name=entity_name)[2].click()
        view.table.row(name=entity_name)[2].widget.item_select('Scan')
        view.flash.assert_no_error()
        view.flash.dismiss()

    def mirror(self, remote, repo, product):
        """Mirror a repository from Flatpak remote.

        :param str remote: name of the remote to mirror from
        :param str repo: name of the repository to be mirrored
        :param str product: name of the product where the repository should be mirrored
        """
        mirror_modal = self.open_mirror_modal(remote=remote, repo=repo)
        self.submit_mirror_modal(mirror_modal=mirror_modal, product=product)

    def open_mirror_modal(self, remote, repo):
        """Open the Mirror Repository modal for a given remote repository."""
        view = self.navigate_to(self, 'All')
        view.search(remote)
        view.table.row(name=remote)['Name'].widget.click()
        view = FlatpakRemoteDetailsView(self.browser)

        view.search(repo)  # in case of many repos
        view.table.row(name=repo)['Mirror'].widget.click()
        mirror_modal = MirrorFlatpakRemoteModal(self.browser)
        mirror_modal.wait_displayed()
        return mirror_modal

    def read_mirror_dependency_alert(self, mirror_modal):
        """Read dependency alert details from the mirror modal."""
        try:
            if not mirror_modal.dependency_alert.is_displayed:
                return None
            return {
                'title': mirror_modal.dependency_alert.title,
                'body': mirror_modal.dependency_info.read(),
                'dependencies': mirror_modal.dependency_repo_names(),
            }
        except NoSuchElementException:
            return None

    def submit_mirror_modal(self, mirror_modal, product, dependencies=None):
        """Submit mirror modal, optionally selecting dependency repositories."""
        for dependency in dependencies or []:
            mirror_modal.select_dependency(dependency)


@navigator.register(FlatpakRemotesEntity, 'All')
class ShowAllFlatpakRemotes(NavigateStep):
    """Navigate to All Flatpak Remotes page."""

    VIEW = FlatpakRemotesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Flatpak Remotes')
