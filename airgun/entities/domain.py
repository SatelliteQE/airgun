from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.utils import retry_navigation
from airgun.views.domain import DomainCreateView
from airgun.views.domain import DomainEditView
from airgun.views.domain import DomainListView


class DomainEntity(BaseEntity):
    endpoint_path = '/domains'

    def create(self, values):
        """Create a new domain."""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit_button.click()
        view.validations.assert_no_errors()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for 'value' and return domain names that match.

        :param value: text to filter (default: no filter)
        """
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Return dict with properties of domain."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values):
        """Update an existing domain."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)

        view.fill(values)
        view.submit_button.click()
        view.validations.assert_no_errors()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def add_parameter(self, entity_name, param_name, param_value):
        """Add new parameter to existing domain entity

        :param entity_name: Domain name to be edited
        :param param_name: Name of a parameter to be added
        :param param_value: Value of a parameter to be added
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.parameters.params.add({'name': param_name, 'value': param_value})
        view.submit_button.click()
        view.validations.assert_no_errors()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def remove_parameter(self, entity_name, param_name):
        """Remove parameter from existing domain entity

        :param entity_name: Domain name to be edited
        :param param_name: Name of a parameter to be removed
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.parameters.params.remove(param_name)
        view.submit_button.click()
        view.validations.assert_no_errors()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete existing domain entity"""
        view = self.navigate_to(self, 'All')
        self.search(entity_name)
        view.table.row(description=entity_name)['Actions'].widget.click(handle_alert=True)
        view.validations.assert_no_errors()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(DomainEntity, 'All')
class ShowAllDomains(NavigateStep):
    """Navigate to All Domains page"""

    VIEW = DomainListView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Infrastructure', 'Domains')


@navigator.register(DomainEntity, 'New')
class AddNewDomain(NavigateStep):
    """Navigate to Create Domain page"""

    VIEW = DomainCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(DomainEntity, 'Edit')
class EditDomain(NavigateStep):
    """Navigate to Edit Domain page

    Args:
        entity_name: name of the domain
    """

    VIEW = DomainEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(description=entity_name)['Description'].widget.click()
