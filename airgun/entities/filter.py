from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.entities.role import RoleEntity
from airgun.views.filter import (
    FilterCreateView,
    FilterDetailsView,
    FiltersView,
)


class FilterEntity(BaseEntity):

    def create(self, role_name, values):
        view = self.navigate_to(self, 'New', role_name=role_name)
        view.fill(values)
        view.submit.click()

    def search(self, role_name, value):
        view = self.navigate_to(self, 'All', role_name=role_name)
        return view.search(value)

    def read(self, role_name, entity_name):
        view = self.navigate_to(
            self, 'Edit', role_name=role_name, entity_name=entity_name)
        return view.read()

    def update(self, role_name, entity_name, values):
        view = self.navigate_to(
            self, 'Edit', role_name=role_name, entity_name=entity_name)
        view.fill(values)
        view.submit.click()

    def delete(self, role_name, entity_name):
        view = self.navigate_to(self, 'All', role_name=role_name)
        view.search(entity_name)
        view.table.row(resource=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()


@navigator.register(FilterEntity, 'All')
class ShowAllFilters(NavigateStep):
    VIEW = FiltersView

    def am_i_here(self, *args, **kwargs):
        role_name = kwargs.get('role_name')
        return (
            self.view.is_displayed
            and self.view.breadcrumb.locations[1] in (
                role_name,
                '{} filters'.format(role_name))
        )

    def step(self, *args, **kwargs):
        role_name = kwargs.get('role_name')
        role_view = self.navigate_to(RoleEntity, 'All')
        role_view.search(role_name)
        role_view.table.row(name=role_name)['Actions'].widget.fill('Filters')


@navigator.register(FilterEntity, 'New')
class AddNewFilter(NavigateStep):
    VIEW = FilterCreateView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All', **kwargs)

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(FilterEntity, 'Edit')
class EditFilter(NavigateStep):
    VIEW = FilterDetailsView

    def am_i_here(self, *args, **kwargs):
        role_name = kwargs.get('role_name')
        return (
            self.view.is_displayed
            and self.view.breadcrumb.locations[1] in (
                role_name,
                'Edit filter for {} filters'.format(role_name))
        )

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All', **kwargs)

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(
            resource=entity_name)['Actions'].widget.fill('Edit')
