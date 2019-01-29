from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.usergroup import (
    UserGroupCreateView,
    UserGroupDetailsView,
    UserGroupsView
)


class UserGroupEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.click(
            handle_alert=True)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def refresh_external_group(self, entity_name, external_group_name):
        """Refresh external group."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.external_groups.table.row(name=external_group_name)['Actions'].widget.click()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(UserGroupEntity, 'All')
class ShowAllUserGroups(NavigateStep):
    VIEW = UserGroupsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'User Groups')


@navigator.register(UserGroupEntity, 'New')
class AddNewUserGroup(NavigateStep):
    VIEW = UserGroupCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(UserGroupEntity, 'Edit')
class EditUserGroup(NavigateStep):
    VIEW = UserGroupDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
