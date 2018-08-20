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

    def read(self, entity_name):
        """Read content host details"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

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

    def search_errata(self, entity_name, errata_id):
        """Search for specific errata applicable for content host"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.errata.search(errata_id)
        return view.errata.table.read()


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
