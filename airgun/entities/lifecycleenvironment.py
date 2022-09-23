from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.utils import retry_navigation
from airgun.views.lifecycleenvironment import LCECreateView
from airgun.views.lifecycleenvironment import LCEEditView
from airgun.views.lifecycleenvironment import LCEView


class LCEEntity(BaseEntity):
    endpoint_path = '/lifecycle_environments'

    def create_environment_path(self, values):
        view = self.navigate_to(self, 'New Path')
        view.fill(values)
        view.submit.click()

    def create_environment(self, values, entity_name):
        view = self.navigate_to(self, 'New Environment', entity_name=entity_name)
        view.fill(values)
        view.submit.click()

    def create(
        self,
        values,
        prior_entity_name=None,
    ):
        """Create new lifecycle environment
        :param values: Parameters to be assigned to lce, at least name should
        be provided
        :param prior_entity_name: Specify entity name which should be a parent
        to lifecycle environment that created in a chain
        """
        if prior_entity_name is not None:
            self.create_environment(values, prior_entity_name)
        else:
            self.create_environment_path(values)

    def read(self, entity_name, widget_names=None):
        """Read specific lifecycle environment details from its Edit page"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def read_all(self):
        """Read all available lifecycle environments details from generic
        lifecycle environments page
        """
        view = self.navigate_to(self, 'All')
        return view.read()

    def update(self, entity_name='Library', values=None):
        """Update existing lifecycle environment values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        filled_values = view.fill(values)
        view.flash.assert_no_error()
        view.flash.dismiss()
        return filled_values

    def delete(self, entity_name):
        """Deletes existing lifecycle environment entity"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.remove.click()
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search_package(self, entity_name, package_name, cv_name=None, repo_name=None):
        """Search for specific package inside lifecycle environment"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.packages.search(package_name, cv=cv_name, repo=repo_name)
        return view.packages.table.read()

    def search_module_stream(self, entity_name, module_name, cv_name=None, repo_name=None):
        """Search for specific module stream inside lifecycle environment"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.module_streams.search(module_name, cv=cv_name, repo=repo_name)
        return view.module_streams.table.read()


@navigator.register(LCEEntity, 'All')
class ShowAllLCE(NavigateStep):
    """Navigate to All Lifecycle Environments page"""

    VIEW = LCEView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Lifecycle Environments')


@navigator.register(LCEEntity, 'New Path')
class AddNewLCEPath(NavigateStep):
    """Navigate to New Lifecycle Environment Path page"""

    VIEW = LCECreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new_path)


@navigator.register(LCEEntity, 'New Environment')
class AddNewLCE(NavigateStep):
    """Navigate to New Lifecycle Environment page"""

    VIEW = LCECreateView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.lce(kwargs.get('entity_name')).new_child.click()


@navigator.register(LCEEntity, 'Edit')
class EditLCE(NavigateStep):
    """Navigate to Edit Lifecycle Environment page

    Args:
        entity_name: name of the lifecycle environment
    """

    VIEW = LCEEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        env_name = kwargs.get('entity_name')
        if env_name == 'Library':
            self.parent.edit_parent_env.click()
        else:
            self.parent.lce(kwargs.get('entity_name')).current_env.click()
