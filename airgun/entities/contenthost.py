from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.contenthost import (
    ContentHostDetailsView,
    ContentHostsView,
    ContentHostTaskDetailsView,
)


class ContentHostEntity(BaseEntity):

    def delete(self, entity_name):
        """Delete existing content host"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)[0].widget.fill(True)
        view.actions.fill('Remove Hosts')
        view.dialog.confirm()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for specific content host"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read_all(self):
        """Read all values from content host title page"""
        view = self.navigate_to(self, 'All')
        return view.read()

    def read(self, entity_name, widget_names=None):
        """Read content host details, optionally read only the widgets in widget_names."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def execute_package_action(self, entity_name, action_type, value):
        """Execute remote package action on a content host

        :param entity_name: content host name to remotely execute package
            action on
        :param action_type: remote action to execute. Can be one of 5: 'Package
            Install', 'Package Update', 'Package Remove', 'Group Install' or
            'Group Remove'
        :param value: Package or package group group name to remotely
            install/upgrade/remove (depending on `action_type`)

        :return: Returns a dict containing task status details
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.packages_actions.action_type.fill(action_type)
        view.packages_actions.name.fill(value)
        view.packages_actions.perform.click()
        view = ContentHostTaskDetailsView(view.browser)
        view.progressbar.wait_for_result()
        return view.read()

    def search_package(self, entity_name, package_name):
        """Search for specific package installed in content host"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.packages_installed.search(package_name)
        return view.packages_installed.table.read()

    def install_errata(self, entity_name, errata_id):
        """Install errata on a content host

        :param name: content host name to apply errata on
        :param errata_id: errata id or title, e.g. 'RHEA-2012:0055'

        :return: Returns a dict containing task status details
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.errata.search(errata_id)
        view.errata.table.row(id=errata_id)[0].widget.fill(True)
        view.errata.apply_selected.fill('Apply Selected')
        view.dialog.confirm()
        view = ContentHostTaskDetailsView(view.browser)
        view.progressbar.wait_for_result()
        return view.read()

    def search_errata(self, entity_name, errata_id, environment=None):
        """Search for specific errata applicable for content host.

        :param str entity_name: the content hosts name.
        :param str errata_id: errata id or title, e.g. 'RHEA-2012:0055'
        :param str optional environment: lifecycle environment to filter by.
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.errata.search(errata_id, lce=environment)
        return view.errata.table.read()

    def export(self):
        """Export content hosts list.

        :return str: path to saved file
        """
        view = self.navigate_to(self, 'All')
        view.export.click()
        return self.browser.save_downloaded_file()

    def add_subscription(self, entity_name, subscription_name):
        """Add a subscription to content host.

        :param str entity_name: the content hosts name.
        :param str subscription_name: The subscription name to add to content host.
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.subscriptions.resources.add(subscription_name)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def update(self, entity_name, values):
        """Update content host values."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(ContentHostEntity, 'All')
class ShowAllContentHosts(NavigateStep):
    """Navigate to All Content Hosts screen."""
    VIEW = ContentHostsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Content Hosts')


@navigator.register(ContentHostEntity, 'Edit')
class EditContentHost(NavigateStep):
    """Navigate to Content Host details screen.

    Args:
        entity_name: name of content host
    """
    VIEW = ContentHostDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
