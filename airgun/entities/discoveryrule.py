from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.discoveryrule import (
    DiscoveryRuleCreateView,
    DiscoveryRuleEditView,
    DiscoveryRulesView,
)


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
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
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
