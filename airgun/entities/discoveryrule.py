from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.discoveryrule import (
    DiscoveryRuleCreateView,
    DiscoveryRuleEditView,
    DiscoveryRulesView,
)
from airgun.views.host import HostsView


class DiscoveryRuleEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def delete(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()

    def read(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def read_all(self):
        view = self.navigate_to(self, 'All')
        return view.table.read()

    def update(self, entity_name, values):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()

    def enable(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.table.row(name=entity_name)['Actions'].widget.fill('Enable')
        self.browser.handle_alert()

    def disable(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.table.row(name=entity_name)['Actions'].widget.fill('Disable')
        self.browser.handle_alert()

    def associated_hosts(self, entity_name, host_name):
        view = self.navigate_to(self, 'All')
        view.table.row(
            name=entity_name)['Actions'].widget.fill('Associated Hosts')
        view = self.navigate_to(self, 'Associate', host_name=host_name)
        return view.table.read()


@navigator.register(DiscoveryRuleEntity, 'All')
class ShowAllDiscoveryRules(NavigateStep):
    VIEW = DiscoveryRulesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Configure', 'Discovery rules')


@navigator.register(DiscoveryRuleEntity, 'New')
class AddNewDiscoveryRule(NavigateStep):
    VIEW = DiscoveryRuleCreateView

    def am_i_here(self, *args, **kwargs):
        return self.view.is_displayed and self.view.name == ''

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)


@navigator.register(DiscoveryRuleEntity, 'Edit')
class EditDiscoveryRule(NavigateStep):
    VIEW = DiscoveryRuleEditView

    def am_i_here(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        return self.view.is_displayed and self.view.name.text == entity_name

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(DiscoveryRuleEntity, 'Associate')
class AssociateHosts(NavigateStep):
    VIEW = HostsView

    def am_i_here(self, *args, **kwargs):
        return self.view.is_displayed and self.view.title == 'Hosts'

    def step(self, *args, **kwargs):
        host_name = kwargs.get('host_name')
        self.view.search(host_name)
