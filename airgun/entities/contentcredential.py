from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.contentcredential import (
    ContentCredentialCreateView,
    ContentCredentialEditView,
    ContentCredentialsTableView,
)


class ContentCredentialEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def delete(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.remove.click()
        view.dialog.confirm()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.fill(values)


@navigator.register(ContentCredentialEntity, 'All')
class ShowAllContentViews(NavigateStep):
    VIEW = ContentCredentialsTableView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Content Credentials')


@navigator.register(ContentCredentialEntity, 'New')
class AddNewContentCredential(NavigateStep):
    VIEW = ContentCredentialCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)


@navigator.register(ContentCredentialEntity, 'Edit')
class EditContentCredential(NavigateStep):
    VIEW = ContentCredentialEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.search(kwargs.get('entity_name'))
        self.parent.edit.click()
