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
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def clone(self, entity_name, values):
        view = self.navigate_to(self, 'Clone', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def lock(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Lock')
        view.flash.assert_no_error()
        view.flash.dismiss()

    def unlock(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Unlock')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def update(self, entity_name, values):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(ReportTemplateEntity, 'All')
class ShowAllReportTemplates(NavigateStep):
    VIEW = ReportTemplatesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Monitor', 'Report Templates')


@navigator.register(ReportTemplateEntity, 'New')
class AddNewReportTemplate(NavigateStep):
    VIEW = ReportTemplateCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(ReportTemplateEntity, 'Edit')
class EditReportTemplate(NavigateStep):
    VIEW = ReportTemplateDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(ReportTemplateEntity, 'Clone')
class CloneReportTemplate(NavigateStep):
    VIEW = ReportTemplateCreateView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Actions'].widget.fill('Clone')
