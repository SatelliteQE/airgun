from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator

from airgun.views.report_template import (
    ReportTemplateCreateView,
    ReportTemplateDetailsView,
    ReportTemplatesView,
)


class ReportTemplateEntity(BaseEntity):

    def create(self, values):
        """Create new report template"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for existing report template"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read report template values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def clone(self, entity_name, values):
        """Clone existing report template"""
        view = self.navigate_to(self, 'Clone', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def lock(self, entity_name):
        """Lock report template for editing"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Lock')
        view.flash.assert_no_error()
        view.flash.dismiss()

    def unlock(self, entity_name):
        """Unlock report template for editing"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Unlock')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def is_locked(self, entity_name):
        """Check if report template is locked for editing"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        return "This template is locked for editing." in view.table.row(
            name=entity_name)['Locked'].widget.browser.element('.').get_property('innerHTML')

    def update(self, entity_name, values):
        """Update report template"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete report template"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(ReportTemplateEntity, 'All')
class ShowAllReportTemplates(NavigateStep):
    """Navigate to all Report Templates screen."""
    VIEW = ReportTemplatesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Monitor', 'Report Templates')


@navigator.register(ReportTemplateEntity, 'New')
class AddNewReportTemplate(NavigateStep):
    """Navigate to Create new Report Template screen."""
    VIEW = ReportTemplateCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(ReportTemplateEntity, 'Edit')
class EditReportTemplate(NavigateStep):
    """Navigate to Edit Report Template screen.

        Args:
            entity_name: name of report template to edit
    """
    VIEW = ReportTemplateDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(ReportTemplateEntity, 'Clone')
class CloneReportTemplate(NavigateStep):
    """Navigate to Create Report Template screen for cloned entity

        Args:
            entity_name: name of report template to clone
    """
    VIEW = ReportTemplateCreateView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Actions'].widget.fill('Clone')
