from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.domain import (
    DomainCreateView,
    DomainEditView,
    DomainListView,
)


class DomainEntity(BaseEntity):
    def create(self, values, assert_no_error=True):
        """
        Create a new domain.
        """
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit_button.click()
        if assert_no_error:
            view.flash.assert_no_error()

    def search(self, value):
        """Search for 'value' and return domain names that match.

        :param value: text to filter (default: no filter)
        """
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        """Return dict with properties of domain."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values, assert_no_error=True):
        """
        Update an existing domain.
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)

        view.fill(values)
        view.submit_button.click()
        if assert_no_error:
            view.flash.assert_no_error()

    def add_parameter(self, entity_name, param_name, param_value,
                      assert_no_error=True):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.parameters.params.add({'name': param_name, 'value': param_value})
        view.submit_button.click()
        if assert_no_error:
            view.flash.assert_no_error()

    def remove_parameter(self, entity_name, param_name, assert_no_error=True):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.parameters.params.remove(param_name)
        view.submit_button.click()
        if assert_no_error:
            view.flash.assert_no_error()

    def delete(self, name, assert_no_error=True):
        view = self.navigate_to(self, 'All')
        self.search(name)
        if not view.table.row_count:
            raise ValueError("Unable to find name '{}'".format(name))
        view.table[0]['Actions'].widget.click()
        self.browser.handle_alert()
        if assert_no_error:
            view.flash.assert_no_error()


@navigator.register(DomainEntity, 'All')
class DomainList(NavigateStep):
    VIEW = DomainListView

    def step(self, *args, **kwargs):
        self.view.menu.select('Infrastructure', 'Domains')


@navigator.register(DomainEntity, 'New')
class AddNewDomain(NavigateStep):
    VIEW = DomainCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.create_button.click()


@navigator.register(DomainEntity, 'Edit')
class EditDomain(NavigateStep):
    VIEW = DomainEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        row = self.parent.table.row(('Description', entity_name))
        row['Description'].widget.click()
