from navmazing import NavigateToSibling
from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.discoveredhosts import DiscoveredHostsView
from airgun.views.discoveryrule import (
    ACTION_COLUMN,
    DiscoveryRuleCreateView,
    DiscoveryRuleEditView,
    DiscoveryRulesView,
)
from airgun.views.host import HostsView


class DiscoveryRuleEntity(BaseEntity):

    def create(self, values):
        """Create new Discovery rule

        :param values: Parameters to be assigned to discovery rule,
            Name, Search, Host Group and Priority should be provided
        """
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete corresponding Discovery rule

        :param str entity_name: name of the corresponding discovery rule
        """
        view = self.navigate_to(self, 'All')
        view.table.row(
            name=entity_name)[ACTION_COLUMN].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def read(self, entity_name):
        """Reads content of corresponding Discovery rule

        :param str entity_name: name of the corresponding discovery rule
        :return: dict representing tabs, with nested dicts representing fields
            and values
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def read_all(self):
        """Reads the whole discovery rules table.

        :return: list of table rows, each row is dict,
            attribute as key with correct value
        """
        view = self.navigate_to(self, 'All')
        return view.table.read()

    def update(self, entity_name, values):
        """Update existing Discovery rule

        :param str entity_name: name of the corresponding discovery rule
        :param values: parameters to be changed at discovery rule
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def enable(self, entity_name):
        """Enable corresponding Discovery rule

        :param str entity_name: name of the corresponding discovery rule
        """
        view = self.navigate_to(self, 'All')
        view.table.row(name=entity_name)[ACTION_COLUMN].widget.fill('Enable')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def disable(self, entity_name):
        """Disable corresponding Discovery rule

        :param str entity_name: name of the corresponding discovery rule
        """
        view = self.navigate_to(self, 'All')
        view.table.row(name=entity_name)[ACTION_COLUMN].widget.fill('Disable')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def discovered_hosts(self, entity_name):
        """View Discovered hosts corresponding to Discovery rule search field.

        :param str entity_name: name of the discovery rule entity
        :return: The discovered hosts view properties
        """
        view = self.navigate_to(self, 'All')
        view.table.row(name=entity_name)[ACTION_COLUMN].widget.fill(
            'Discovered Hosts')
        discovered_hosts_view = DiscoveredHostsView(
            self.browser, logger=view.logger)
        wait_for(
            lambda: discovered_hosts_view.is_displayed is True,
            timeout=60,
            delay=1,
            logger=discovered_hosts_view.logger
        )
        discovered_hosts_view.flash.assert_no_error()
        discovered_hosts_view.flash.dismiss()
        return discovered_hosts_view.read()

    def associated_hosts(self, entity_name):
        """View Discovery rule associated hosts.

        :param entity_name: name of the discovery rule entity
        :return: The hosts view properties
        """
        # Associated Hosts
        view = self.navigate_to(self, 'All')
        view.table.row(name=entity_name)[ACTION_COLUMN].widget.fill(
            'Associated Hosts')
        hosts_view = HostsView(self.browser, logger=view.logger)
        wait_for(
            lambda: hosts_view.is_displayed is True,
            timeout=60,
            delay=1,
            logger=hosts_view.logger
        )
        hosts_view.flash.assert_no_error()
        hosts_view.flash.dismiss()
        return hosts_view.read()


@navigator.register(DiscoveryRuleEntity, 'All')
class ShowAllDiscoveryRules(NavigateStep):
    """Navigate to All Discovery rules screen."""
    VIEW = DiscoveryRulesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Configure', 'Discovery rules')


@navigator.register(DiscoveryRuleEntity, 'New')
class AddNewDiscoveryRule(NavigateStep):
    """Navigate to Create Discovery rule page."""
    VIEW = DiscoveryRuleCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)


@navigator.register(DiscoveryRuleEntity, 'Edit')
class EditDiscoveryRule(NavigateStep):
    """Navigate to Edit Discovery rule page.

        Args:
            entity_name: name of the discovery rule
    """
    VIEW = DiscoveryRuleEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.table.row(name=entity_name)['Name'].widget.click()
