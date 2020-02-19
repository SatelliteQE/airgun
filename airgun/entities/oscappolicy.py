from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.oscappolicy import SCAPPoliciesView
from airgun.views.oscappolicy import SCAPPolicyCreateView
from airgun.views.oscappolicy import SCAPPolicyDetailsView
from airgun.views.oscappolicy import SCAPPolicyEditView


class OSCAPPolicyEntity(BaseEntity):
    endpoint_path = '/compliance/policies'

    def create(self, values):
        """Creates new OSCAP Policy

        :param values: Parameters to be assigned to new SCAP policy,
            mandatory values are Name, Scap Content and Period,
            with chosen date when policy is going to repeat
        """
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.host_group.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete corresponding SCAP Policy

        :param entity_name: name of the corresponding SCAP Policy
        """
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, entity_name):
        """Search for SCAP Policy

        :param entity_name: name of the corresponding SCAP Policy
        :return: result of the SCAP Policy search
        """
        view = self.navigate_to(self, 'All')
        return view.search(entity_name)

    def details(self, entity_name, widget_names=None):
        """Read the content from corresponding SCAP Policy dashboard,
            clicking on the Name of SCAP Policy shows the dashboard

        :param entity_name:
        :return: dictionary with values from SCAP Policy Details View
        """
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def read(self, entity_name, widget_names=None):
        """Reads the values of corresponding SCAP Policy - edit menu

        :param entity_name: specifies corresponding SCAP Policy
        :return: dict representing tabs, with nested dicts representing fields
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values):
        """Updates instance of SCAP Policy with new values

        :param entity_name: specifies corresponding SCAP Policy
        :param values: updates individual parameters of corresponding
            SCAP Policy
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(OSCAPPolicyEntity, 'All')
class ShowAllSCAPPolicies(NavigateStep):
    """Navigate to All SCAP Policies screen."""
    VIEW = SCAPPoliciesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Policies')


@navigator.register(OSCAPPolicyEntity, 'New')
class NewSCAPPolicy(NavigateStep):
    """Navigate to upload new SCAP Policies page."""
    VIEW = SCAPPolicyCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(OSCAPPolicyEntity, 'Edit')
class EditSCAPPolicy(NavigateStep):
    """Navigate to edit existing SCAP Policy page.

        Args:
        entity_name: name of SCAP policy
    """
    VIEW = SCAPPolicyEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Actions'].widget.fill('Edit')


@navigator.register(OSCAPPolicyEntity, 'Details')
class DetailsSCAPPolicy(NavigateStep):
    """To get data from SCAPPolicyDetail view

        Args:
        entity_name: name of SCAP policy
    """
    VIEW = SCAPPolicyDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
