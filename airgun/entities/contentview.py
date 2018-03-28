from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.contentview import (
    ContentViewCreateView,
    ContentViewEditView,
    ContentViewTableView,
)


class ContentViewEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def delete(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.action_list.fill('Remove Content View')
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


@navigator.register(ContentViewEntity, 'All')
class ShowAllContentViews(NavigateStep):
    VIEW = ContentViewTableView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Content Views')


@navigator.register(ContentViewEntity, 'New')
class AddNewContentView(NavigateStep):
    VIEW = ContentViewCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)


@navigator.register(ContentViewEntity, 'Edit')
class EditContentView(NavigateStep):
    VIEW = ContentViewEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.search(kwargs.get('entity_name'))
        self.parent.edit.click()
