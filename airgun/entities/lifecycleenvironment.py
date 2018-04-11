from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.lifecycleenvironment import (
    LCECreateView,
    LCEEditView,
    LCEView,
)


class LCEEntity(BaseEntity):

    def create_environment_path(self, values):
        view = self.navigate_to(self, 'New Path')
        view.fill(values)
        view.submit.click()

    def create_environment(self, entity_name, values):
        view = self.navigate_to(
            self, 'New Environment', entity_name=entity_name)
        view.fill(values)
        view.submit.click()

    def read(self):
        view = self.navigate_to(self, 'All')
        return view.read()

    def update_parent_path(self, values):
        view = self.navigate_to(self, 'Edit')
        return view.fill(values)

    def update_env(self, entity_name, values):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.fill(values)


@navigator.register(LCEEntity, 'All')
class ShowAllLCE(NavigateStep):
    VIEW = LCEView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Lifecycle Environments')


@navigator.register(LCEEntity, 'New Path')
class AddNewEnvironmentPath(NavigateStep):
    VIEW = LCECreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new_path)


@navigator.register(LCEEntity, 'New Environment')
class AddNewEnvironment(NavigateStep):
    VIEW = LCECreateView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.LCE(kwargs.get('entity_name')).new_child.click()


@navigator.register(LCEEntity, 'Edit')
class EditParentEnvironmentPath(NavigateStep):
    VIEW = LCEEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.edit_parent_env.click()


@navigator.register(LCEEntity, 'Edit')
class EditEnvironment(NavigateStep):
    VIEW = LCEEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.LCE(kwargs.get('entity_name')).current_env.click()
