from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.ansible_role import AnsibleRolesImportView
from airgun.views.ansible_role import AnsibleRolesView


class AnsibleRolesEntity(BaseEntity):
    """Main Ansible roles entity"""

    endpoint_path = '/ansible/ansible_roles'

    def search(self, value):
        """Search for existing Ansible Role"""
        view = self.navigate_to(self, 'All')
        view.search(value)
        return view.table.read()

    def delete(self, entity_name):
        """Delete Ansible Role from Satellite"""
        # This method currently relies on searching for a specific role as
        # directly accessing the 'Name' column is not possible due to the
        # presence of the `▲` character used for sorting that column in the table
        # header cell. The Satellite UX team is planning to address this in a
        # future release, likely by wrapping the sort character in a separate
        # span tag from the column header text.
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row()['Actions'].widget.fill('Delete')
        view.dialog.confirm_dialog.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    @property
    def imported_roles_count(self):
        """Return the number of Ansible roles currently imported into Satellite"""
        view = self.navigate_to(self, 'All')
        # Before any roles have been imported, no table or pagination widget are
        # present on the page
        # Applying wait_displayed for the page to get rendered
        view.wait_displayed()
        return int(view.total_imported_roles.read())

    def import_all_roles(self):
        """Import all available roles and return the number of roles
        that were available at import time
        """
        view = self.navigate_to(self, 'Import')
        available_roles_count = int(view.total_available_roles.read())
        view.select_all.fill(True)
        view.submit.click()
        return available_roles_count


@navigator.register(AnsibleRolesEntity, 'All')
class ShowAllRoles(NavigateStep):
    """Navigate to the Ansible Roles page"""

    VIEW = AnsibleRolesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Configure', 'Ansible', 'Roles')


@navigator.register(AnsibleRolesEntity, 'Import')
class ImportAnsibleRole(NavigateStep):
    """Navigate to the Import Roles page"""

    VIEW = AnsibleRolesImportView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.import_button.click()
