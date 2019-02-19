from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.entities.role import RoleEntity
from airgun.views.filter import (
    FilterCreateView,
    FilterDetailsView,
    FiltersView,
)


class FilterEntity(BaseEntity):

    def create(self, role_name, values):
        """Create new filter for specific role"""
        view = self.navigate_to(self, 'New', role_name=role_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, role_name, value):
        """Search for filter assigned to the role"""
        view = self.navigate_to(self, 'All', role_name=role_name)
        return view.search(value)

    def read(self, role_name, entity_name, widget_names=None):
        """Read values for specific filter"""
        view = self.navigate_to(
            self, 'Edit', role_name=role_name, entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def read_all(self, role_name):
        """Read all the available role filters table values"""
        view = self.navigate_to(self, 'All', role_name=role_name)
        return view.table.read()

    def read_permissions(self, role_name):
        """Return all role filters permissions as a dict with resources as keys and permission
        names as values.
        """
        rows = self.read_all(role_name)
        permissions = {}
        for row in rows:
            resource = row['Resource']
            if resource not in permissions:
                permissions[resource] = []
            permissions[resource].extend(row['Permissions'].split(', '))
        return permissions

    def update(self, role_name, entity_name, values):
        """Update filter values"""
        view = self.navigate_to(
            self, 'Edit', role_name=role_name, entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, role_name, entity_name):
        """Delete specific filter from role"""
        view = self.navigate_to(self, 'All', role_name=role_name)
        view.search(entity_name)
        view.table.row(resource=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(FilterEntity, 'All')
class ShowAllFilters(NavigateStep):
    """Navigate to All Role Filters page by pressing 'Filters' button on Roles
    List view.

    Args:
        role_name: name of role
    """
    VIEW = FiltersView

    def am_i_here(self, *args, **kwargs):
        role_name = kwargs.get('role_name')
        return (
            self.view.is_displayed
            and self.view.breadcrumb.locations[1] in (
                role_name,
                '{} filters'.format(role_name))
        )

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(RoleEntity, 'All', **kwargs)

    def step(self, *args, **kwargs):
        role_name = kwargs.get('role_name')
        self.parent.search(role_name)
        self.parent.table.row(name=role_name)['Actions'].widget.fill('Filters')


@navigator.register(FilterEntity, 'New')
class AddNewFilter(NavigateStep):
    """Navigate to role's Create Filter page

    Args:
        role_name: name of role
        entity_name: name of filter
    """
    VIEW = FilterCreateView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All', **kwargs)

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(FilterEntity, 'Edit')
class EditFilter(NavigateStep):
    """Navigate to role's Edit Filter page

    Args:
        role_name: name of role
        entity_name: name of filter
    """
    VIEW = FilterDetailsView

    def am_i_here(self, *args, **kwargs):
        role_name = kwargs.get('role_name')
        return (
            self.view.is_displayed
            and self.view.breadcrumb.locations[1] in (
                role_name,
                'Edit filter for {} filters'.format(role_name))
        )

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All', **kwargs)

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(
            resource=entity_name)['Actions'].widget.fill('Edit')
