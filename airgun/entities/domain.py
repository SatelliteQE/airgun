from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.domain import (
    DomainCreateView,
    DomainEditView,
    DomainListView,
)


def assert_no_errors_in_view(view):
    """
    Check that there's no elements of class "has-error" in the view

    There can be elements that have an error, and there can also be
    error message blocks. If errors are found on the page, then
    we will search for any displayed error messages and print
    their text in the AssertionError

    TODO: Move this somewhere for general use by other entities?
    """
    error_elements = view.browser.elements(
        ".//*[contains(@class,'has-error') "
        "and not(contains(@style,'display:none'))]"
    )
    if error_elements:
        error_msgs = view.browser.elements(
            ".//*[(contains(@class,'error-msg-block') "
            "or contains(@class,'error-message')) "
            "and not(contains(@style,'display:none'))]"
        )
        error_msgs = [view.browser.text(error_msg) for error_msg in error_msgs]
        raise AssertionError(
            "errors present on page, displayed messages: {}".format(error_msgs)
        )


class DomainEntity(BaseEntity):
    def create(self, values, assert_no_errors=True):
        """
        Create a new domain.
        """
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit_button.click()
        if assert_no_errors:
            view.flash.assert_no_error()
            assert_no_errors_in_view(view)

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

    def update(self, entity_name, values, assert_no_errors=True):
        """
        Update an existing domain.
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)

        view.fill(values)
        view.submit_button.click()
        if assert_no_errors:
            view.flash.assert_no_error()
            assert_no_errors_in_view(view)

    def add_parameter(self, entity_name, param_name, param_value,
                      assert_no_errors=True):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.parameters.params.add({'name': param_name, 'value': param_value})
        view.submit_button.click()
        if assert_no_errors:
            view.flash.assert_no_error()
            assert_no_errors_in_view(view)

    def remove_parameter(self, entity_name, param_name, assert_no_errors=True):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.parameters.params.remove(param_name)
        view.submit_button.click()
        if assert_no_errors:
            view.flash.assert_no_error()
            assert_no_errors_in_view(view)

    def delete(self, name, assert_no_errors=True):
        view = self.navigate_to(self, 'All')
        self.search(name)
        if not view.table.row_count:
            raise ValueError("Unable to find name '{}'".format(name))
        view.table[0]['Actions'].widget.click()
        self.browser.handle_alert()
        if assert_no_errors:
            view.flash.assert_no_error()
            assert_no_errors_in_view(view)


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
