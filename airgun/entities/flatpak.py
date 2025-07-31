from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.flatpak import (
    CreateFlatpakRemoteModal,
    EditFlatpakRemoteModal,
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
        view.wait_displayed()
        return view.search(value)

    def read(self, widget_names=None):
        """Read all values for widgets in the view.

        :param list widget_names: list of widgets to read
        :return: dict of widget names and their values
        :rtype: dict
        """
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        return view.read(widget_names=widget_names)

    def read_table(self):
        """Read the table of Flatpak remotes.

        :return: list of table rows
        :rtype: list
        """
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        return view.table.read()

    def read_remote_details(self, name, repo_search=None):
        """
        Read details from the Flatpak remote details page

        Args:
            name (str): Name of the flatpak remote to be read
            repo_search (str, optional): Name of scanned remote repository to be searched
        """
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        view.search(name)
        view.table.row(name=name)['Name'].widget.click()
        view = FlatpakRemoteDetailsView(self.browser)
        view.wait_displayed()
        if repo_search:
            view.search(repo_search)
        return view.read()

    def create(self, values):
        """Create a Flatpak remote.

        :param dict values: values to create the remote with
        """
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        view.create_btn.click()
        view = CreateFlatpakRemoteModal(self.browser)
        view.wait_displayed()
        view.fill(values)
        view.create_btn.click()

    def edit(self, entity_name, values):
        """Edit a Flatpak remote.

        :param str entity_name: name of the remote to edit
        :param dict values: values to update the remote with
        """
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        view.table.row(name=entity_name)[2].click()
        view.table.row(name=entity_name)[2].widget.item_select('Edit')
        view = EditFlatpakRemoteModal(self.browser)
        view.wait_displayed()
        view.fill(values)
        view.update_btn.click()

    def delete(self, entity_name):
        """Delete a Flatpak remote.

        :param str entity_name: name of the remote to delete
        """
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        view.table.row(name=entity_name)[2].click()
        view.table.row(name=entity_name)[2].widget.item_select('Delete')
        # self.browser.handle_alert()  # TODO uncomment once confirm dialog is in snap
        view.flash.assert_no_error()
        view.flash.dismiss()

    def scan(self, entity_name):
        """Scan a Flatpak remote.

        :param str entity_name: name of the remote to scan
        """
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
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
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        view.search(remote)
        view.table.row(name=remote)['Name'].widget.click()
        view = FlatpakRemoteDetailsView(self.browser)
        view.wait_displayed()
        view.search(repo)  # in case of many repos
        view.table.row(name=repo)['Mirror'].widget.click()
        view = MirrorFlatpakRemoteModal(self.browser)
        view.wait_displayed()
        view.searchbar.fill(product)
        self.browser.plugin.ensure_page_safe()
        view.mirror_btn.click()


@navigator.register(FlatpakRemotesEntity, 'All')
class ShowAllFlatpakRemotes(NavigateStep):
    """Navigate to All Flatpak Remotes page."""

    VIEW = FlatpakRemotesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Flatpak Remotes')
