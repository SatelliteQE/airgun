from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.user import UserDetailsView, UsersView


class UserEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

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

    def delete(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(username=entity_name)['Actions'].widget.click(
            handle_alert=True)


@navigator.register(UserEntity, 'All')
class ShowAllUsers(NavigateStep):
    VIEW = UsersView

    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'Users')


@navigator.register(UserEntity, 'New')
class AddNewUser(NavigateStep):
    VIEW = UserDetailsView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(UserEntity, 'Edit')
class EditUser(NavigateStep):
    VIEW = UserDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(username=entity_name)['Username'].widget.click()
