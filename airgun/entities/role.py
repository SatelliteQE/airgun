from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.role import RoleDetailsView, RolesView


class RoleEntity(BaseEntity):

    def create(self, values):
        """Create new role"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        """Read role values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values):
        """Update role with provided values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()

    def delete(self, entity_name):
        """Delete role from the system"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()


@navigator.register(RoleEntity, 'All')
class ShowAllRoles(NavigateStep):
    VIEW = RolesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'Roles')


@navigator.register(RoleEntity, 'New')
class AddNewRole(NavigateStep):
    VIEW = RoleDetailsView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(RoleEntity, 'Edit')
class EditRole(NavigateStep):
    VIEW = RoleDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
