from navmazing import NavigateToSibling
from widgetastic.exceptions import NoSuchElementException

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.discoveredhosts import DiscoveredHostsView
from airgun.views.discoveryrule import (
    DiscoveryRuleCreateView,
    DiscoveryRuleEditView,
    DiscoveryRulesView,
)
from airgun.views.host import HostsView


class DiscoveryRuleEntity(BaseEntity):
    endpoint_path = '/discovery_rules'

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
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def read(self, entity_name, widget_names=None):
        """Reads content of corresponding Discovery rule

        :param str entity_name: name of the corresponding discovery rule
        :return: dict representing tabs, with nested dicts representing fields
            and values
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

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
        view.table.row(name=entity_name)['Actions'].widget.fill('Enable')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def disable(self, entity_name):
        """Disable corresponding Discovery rule

        :param str entity_name: name of the corresponding discovery rule
        """
        view = self.navigate_to(self, 'All')
        view.table.row(name=entity_name)['Actions'].widget.fill('Disable')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def read_discovered_hosts(self, entity_name, widget_names=None):
        """Read Discovered hosts corresponding to Discovery rule search field.

        :param str entity_name: name of the discovery rule entity
        :return: The discovered hosts view properties
        """
        view = self.navigate_to(
            self, 'Hosts', action_name='Discovered Hosts', entity_name=entity_name
        )
        view.flash.assert_no_error()
        view.flash.dismiss()
        return view.read(widget_names=widget_names)

    def read_associated_hosts(self, entity_name, widget_names=None):
        """Read Discovery rule associated hosts.

        :param entity_name: name of the discovery rule entity
        :return: The hosts view properties
        """
        view = self.navigate_to(
            self, 'Hosts', action_name='Associated Hosts', entity_name=entity_name
        )
        view.flash.assert_no_error()
        view.flash.dismiss()
        return view.read(widget_names=widget_names)


@navigator.register(DiscoveryRuleEntity, 'All')
class ShowAllDiscoveryRules(NavigateStep):
    """Navigate to All Discovery rules screen."""

    VIEW = DiscoveryRulesView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Configure', 'Discovery Rules')


@navigator.register(DiscoveryRuleEntity, 'New')
class AddNewDiscoveryRule(NavigateStep):
    """Navigate to Create Discovery rule page."""

    VIEW = DiscoveryRuleCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        try:
            self.parent.new.click()
        except NoSuchElementException:
            self.parent.new_on_blank_page.click()


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


@navigator.register(DiscoveryRuleEntity, 'Hosts')
class DiscoveredRuleHosts(NavigateStep):
    """Navigate to discovery rule entity Associated/Discovered Hosts page by
    clicking on the action name of the entity dropdown button.

        Args:
            action_name: the action name to select from dropdown button.
            entity_name: name of the discovery rule entity.
    """

    ACTIONS_VIEWS = {'Associated Hosts': HostsView, 'Discovered Hosts': DiscoveredHostsView}

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        action_name = kwargs.get('action_name')
        self.VIEW = self.ACTIONS_VIEWS.get(action_name)
        if not self.VIEW:
            raise ValueError(
                f'Please provide a valid action name. action_name: "{action_name}" not found.'
            )
        entity_name = kwargs.get('entity_name')
        self.parent.table.row(name=entity_name)['Actions'].widget.fill(action_name)
