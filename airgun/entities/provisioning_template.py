from navmazing import NavigateToSibling
from widgetastic.exceptions import NoSuchElementException

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.provisioning_template import (
    ProvisioningTemplateCreateView,
    ProvisioningTemplateDetailsView,
    ProvisioningTemplatesView,
)


class ProvisioningTemplateEntity(BaseEntity):
    endpoint_path = '/templates/provisioning_templates'

    def create(self, values):
        """Create new provisioning template"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for existing provisioning template"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read provisioning template values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def clone(self, entity_name, values):
        """Clone existing provisioning template"""
        view = self.navigate_to(self, 'Clone', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def lock(self, entity_name):
        """Lock provisioning template for editing"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Lock')
        view.flash.assert_no_error()
        view.flash.dismiss()

    def unlock(self, entity_name):
        """Unlock provisioning template for editing"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Unlock')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def is_locked(self, entity_name):
        """Check if provisioning template is locked for editing"""
        view = self.navigate_to(self, 'All')
        view.search(f'name="{entity_name}"')
        try:
            return "This template is locked for editing." in view.table.row(name=entity_name)[
                'Locked'
            ].widget.browser.element('.').get_property('innerHTML')
        except NoSuchElementException:
            return False

    def is_supported(self, entity_name):
        """Check if provisioning template is supported or not"""
        view = self.navigate_to(self, 'All')
        view.search(f'name="{entity_name}"')
        try:
            return "Supported by Red Hat" in view.table.row(name=entity_name)[
                'Name'
            ].widget.browser.element('./img').get_attribute('title')
        except NoSuchElementException:
            return False

    def update(self, entity_name, values):
        """Update provisioning template"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete provisioning template"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(ProvisioningTemplateEntity, 'All')
class ShowAllProvisioningTemplates(NavigateStep):
    """Navigate to all Provisioning Templates screen."""

    VIEW = ProvisioningTemplatesView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Provisioning Templates')


@navigator.register(ProvisioningTemplateEntity, 'New')
class AddNewProvisioningTemplate(NavigateStep):
    """Navigate to Create new Provisioning Template screen."""

    VIEW = ProvisioningTemplateCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(ProvisioningTemplateEntity, 'Edit')
class EditProvisioningTemplate(NavigateStep):
    """Navigate to Edit Provisioning Template screen.

    Args:
        entity_name: name of provisioning template to edit
    """

    VIEW = ProvisioningTemplateDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(ProvisioningTemplateEntity, 'Clone')
class CloneProvisioningTemplate(NavigateStep):
    """Navigate to Create Provisioning Template screen for cloned entity

    Args:
        entity_name: name of provisioning template to clone
    """

    VIEW = ProvisioningTemplateCreateView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Actions'].widget.fill('Clone')
