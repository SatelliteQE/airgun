from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.user import UserCreateView
from airgun.views.user import UserDetailsView
from airgun.views.user import UsersView
from wait_for import wait_for

class UserEntity(BaseEntity):
    endpoint_path = '/users'

    def create(self, values):
        """Create new user entity"""
        view = self.navigate_to(self, 'New')
        wait_for(
            lambda: UserCreateView(self.browser).is_displayed is True,
            timeout=60,
            delay=1,
        )
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for user entity"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read all values for created user entity"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values):
        """Update necessary values for user"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Remove existing user entity"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(username=entity_name)['Actions'].widget.click(
            handle_alert=True)
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(UserEntity, 'All')
class ShowAllUsers(NavigateStep):
    """Navigate to All Users page"""
    VIEW = UsersView

    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'Users')


@navigator.register(UserEntity, 'New')
class AddNewUser(NavigateStep):
    """Navigate to Create User page"""
    VIEW = UserCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(UserEntity, 'Edit')
class EditUser(NavigateStep):
    """Navigate to Edit User page

    Args:
        entity_name: name of the user
    """
    VIEW = UserDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(username=entity_name)['Username'].widget.click()
