from navmazing import NavigateToSibling
from widgetastic.widget import RowNotFound

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.ldapauthentication import (
    LDAPAuthenticationCreateView,
    LDAPAuthenticationEditView,
    LDAPAuthenticationsView,
)


class LDAPAuthenticationEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def read(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def read_table_row(self, entity_name):
        view = self.navigate_to(self, 'All')
        try:
            row_value = view.table.row(name=entity_name).read()
        except RowNotFound:
            row_value = None
        return row_value

    def update(self, entity_name, values):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()

    def delete(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.table.row(name=entity_name)['Actions'].widget.click(
            handle_alert=True)


@navigator.register(LDAPAuthenticationEntity, 'All')
class ShowAllLDAPSources(NavigateStep):
    VIEW = LDAPAuthenticationsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'LDAP Authentication')


@navigator.register(LDAPAuthenticationEntity, 'New')
class AddNewLDAPSource(NavigateStep):
    VIEW = LDAPAuthenticationCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(LDAPAuthenticationEntity, 'Edit')
class EditLDAPSource(NavigateStep):
    VIEW = LDAPAuthenticationEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.table.row(name=entity_name)['Name'].widget.click()
