from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.utils import retry_navigation
from airgun.views.role import RoleCloneView
from airgun.views.role import RoleCreateView
from airgun.views.role import RoleEditView
from airgun.views.role import RolesView


class RoleEntity(BaseEntity):
    endpoint_path = '/roles'

    def create(self, values):
        """Create new role"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read role values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values):
        """Update role with provided values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete role from the system"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        view.dialog.confirm()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def clone(self, entity_name, values):
        """Clone role with entity_name with new properties values"""
        view = self.navigate_to(self, 'Clone', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(RoleEntity, 'All')
class ShowAllRoles(NavigateStep):
    """Navigate to All Roles page"""

    VIEW = RolesView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'Roles')


@navigator.register(RoleEntity, 'New')
class AddNewRole(NavigateStep):
    """Navigate to Create New Role page"""

    VIEW = RoleCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(RoleEntity, 'Edit')
class EditRole(NavigateStep):
    """Navigate to Edit Role page

    Args:
        entity_name: name of role
    """

    VIEW = RoleEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(RoleEntity, 'Clone')
class CloneRole(NavigateStep):
    """Navigate to Clone Role page"""

    VIEW = RoleCloneView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Actions'].widget.fill('Clone')
