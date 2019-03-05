from airgun.navigation import navigator
from airgun.entities.template import (
        TemplateEntity,
        ShowAllTemplates,
        AddNewTemplate,
        EditTemplate,
        CloneTemplate,
)
from airgun.views.report_template import (
    ReportTemplateCreateView,
    ReportTemplateDetailsView,
    ReportTemplatesView,
)


class ReportTemplateEntity(TemplateEntity):
    pass


@navigator.register(ReportTemplateEntity, 'All')
class ShowAllReportTemplates(ShowAllTemplates):
    VIEW = ReportTemplatesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Monitor', 'Report Templates')


@navigator.register(ReportTemplateEntity, 'New')
class AddNewReportTemplate(AddNewTemplate):
    VIEW = ReportTemplateCreateView


@navigator.register(ReportTemplateEntity, 'Edit')
class EditReportTemplate(EditTemplate):
    VIEW = ReportTemplateDetailsView


@navigator.register(ReportTemplateEntity, 'Clone')
class CloneReportTemplate(CloneTemplate):
    VIEW = ReportTemplateCreateView
