from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.ansible_variable import AnsibleVariablesView
from airgun.views.ansible_variable import NewAnsibleVariableView


class AnsibleVariablesEntity(BaseEntity):
    """Main Ansible variables entity"""

    endpoint_path = '/ansible/ansible_variables'

    def search(self, value):
        """Search for existing Ansible variable"""
        view = self.navigate_to(self, 'All')
        view.search(value)
        return view.table.read()

    def delete(self, entity_name):
        """Delete Ansible variable from Satellite"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.click(handle_alert=True)
        view.confirm.confirm_dialog.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def read_total_variables(self):
        """Returns the number of Ansible variables currently in Satellite"""
        view = self.navigate_to(self, 'All')
        return view.total_variables.read()

    def create(self, values):
        """Create a new Ansible variable with minimum inputs"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def create_with_overrides(self, values):
        """Create a new Ansible variable that is managed by Satellite"""
        view = self.navigate_to(self, 'New')
        view.override.fill(True)
        view.expand()
        view.matcher_section.before_fill(values)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(AnsibleVariablesEntity, 'All')
class ShowAllVariables(NavigateStep):
    """Navigate to Ansible Variables page"""

    VIEW = AnsibleVariablesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Configure', 'Variables')


@navigator.register(AnsibleVariablesEntity, 'New')
class NewAnsibleVariable(NavigateStep):
    """Navigate to Create Ansible Variable page"""

    VIEW = NewAnsibleVariableView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new_variable.click()
