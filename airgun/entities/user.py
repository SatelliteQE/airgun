from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.user import UserDetailsView, UserView


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
        view.searchbox.search(entity_name)
        view.delete.click(handle_alert=True)


@navigator.register(UserEntity, 'All')
class ShowAllUsers(NavigateStep):
    VIEW = UserView

    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'Users')


@navigator.register(UserEntity, 'New')
class AddNewUser(NavigateStep):
    VIEW = UserDetailsView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.view.browser.wait_for_element(
            self.parent.new, ensure_page_safe=True)
        self.parent.browser.click(self.parent.new)


@navigator.register(UserEntity, 'Edit')
class EditUser(NavigateStep):
    VIEW = UserDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.search(kwargs.get('entity_name'))
        self.parent.browser.wait_for_element(
            self.parent.edit, ensure_page_safe=True)
        self.parent.edit.click()
