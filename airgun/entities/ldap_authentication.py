from navmazing import NavigateToSibling
from widgetastic.exceptions import NoSuchElementException, RowNotFound

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.ldapauthentication import (
    LDAPAuthenticationCreateView,
    LDAPAuthenticationEditView,
    LDAPAuthenticationsView,
)


class LDAPAuthenticationEntity(BaseEntity):
    endpoint_path = '/auth_sources'

    def create(self, values):
        """Create new LDAP Authentication source"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def read(self, entity_name, widget_names=None):
        """Read all values for existing LDAP Authentication source"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def read_table_row(self, entity_name):
        """Read values for corresponding table row from LDAP Authentication
        title page. Return None in case row is not present in the table
        """
        view = self.navigate_to(self, 'All')
        try:
            row_value = view.table.row(name=entity_name).read()
        except (RowNotFound, NoSuchElementException):
            row_value = None
        return row_value

    def update(self, entity_name, values):
        """Update existing LDAP Authentication source"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete corresponding LDAP Authentication source"""
        view = self.navigate_to(self, 'All')
        view.table.row(name=entity_name)['Actions'].widget.click(handle_alert=True)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def test_connection(self, values):
        """Testing FQDN for test connection"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.ldap_server.text_connection.click()
        view.flash.assert_no_error()

    def read_auth_source_counts(self, auth_source_type):
        """Read values for corresponding auth source card count"""
        view = self.navigate_to(self, 'All')
        if auth_source_type.lower() in ('internal', 'external', 'ldap'):
            return getattr(view, auth_source_type.lower()).count


@navigator.register(LDAPAuthenticationEntity, 'All')
class ShowAllLDAPSources(NavigateStep):
    """Navigate to All LDAP Authentication sources screen."""

    VIEW = LDAPAuthenticationsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'Authentication Sources')


@navigator.register(LDAPAuthenticationEntity, 'New')
class AddNewLDAPSource(NavigateStep):
    """Navigate to Create LDAP Authentication screen."""

    VIEW = LDAPAuthenticationCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.ldap.select_kebab.item_select('Create')


@navigator.register(LDAPAuthenticationEntity, 'Edit')
class EditLDAPSource(NavigateStep):
    """Navigate to Edit LDAP Authentication screen.

    Args:
        entity_name: name of LDAP Authenication source
    """

    VIEW = LDAPAuthenticationEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.table.row(name=entity_name)['Name'].widget.click()
