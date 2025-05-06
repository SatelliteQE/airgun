from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.flatpak import FlatpakRemotesView


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

    def edit(self, entity_name, values):
        """Edit a Flatpak remote.

        :param str entity_name: name of the remote to edit
        :param dict values: values to update the remote with
        """
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        view.table.row(name=entity_name)[2].click()
        view.table.row(name=entity_name)[2].widget.item_select('Edit')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete a Flatpak remote.

        :param str entity_name: name of the remote to delete
        """
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        view.table.row(name=entity_name)[2].click()
        view.table.row(name=entity_name)[2].widget.item_select('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(FlatpakRemotesEntity, 'All')
class ShowAllFlatpakRemotes(NavigateStep):
    """Navigate to All Flatpak Remotes page."""

    VIEW = FlatpakRemotesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Flatpak Remotes')
