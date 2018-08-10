from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.job_template import (
    JobTemplateCreateView,
    JobTemplateEditView,
    JobTemplatesView,
)


class JobTemplateEntity(BaseEntity):

    def create(self, values):
        """Create new job template"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for specific job template"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        """Read all values for existing job template"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values):
        """Update necessary values for existing job template"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def clone(self, entity_name, values):
        """Clone existing job template"""
        view = self.navigate_to(self, 'Clone', entity_name=entity_name)
        view.fill(values)
        view.submit.click()

    def delete(self, entity_name):
        """Delete job template"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(JobTemplateEntity, 'All')
class ShowAllTemplates(NavigateStep):
    """Navigate to All Job Templates screen."""
    VIEW = JobTemplatesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Job templates')


@navigator.register(JobTemplateEntity, 'New')
class AddNewTemplate(NavigateStep):
    """Navigate to Create new Job Template screen."""
    VIEW = JobTemplateCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(JobTemplateEntity, 'Edit')
class EditTemplate(NavigateStep):
    """Navigate to Edit Job Template screen.

         Args:
            entity_name: name of job template
    """
    VIEW = JobTemplateEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(JobTemplateEntity, 'Clone')
class CloneTemplate(NavigateStep):
    """Navigate to Clone Job Template screen.

         Args:
            entity_name: name of job template to be cloned
    """
    VIEW = JobTemplateCreateView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Actions'].widget.fill('Clone')
