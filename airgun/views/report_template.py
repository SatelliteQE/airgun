from widgetastic.widget import (
        Checkbox,
        Text,
        TextInput,
        View,
)

from airgun.views.template import (
    TemplatesView,
    TemplateDetailsView,
    TemplateCreateView,
)
from airgun.views.common import (
    SatTab,
    TemplateEditor,
)
from airgun.widgets import (
    MultiSelect,
)


class ReportTemplatesView(TemplatesView):
    title = Text("//h1[contains(., 'Report Templates')]")
    new = Text("//a[contains(@href, '/templates/report_templates/new')]")


class ReportTemplateDetailsView(TemplateDetailsView):
    FORM = "//form[contains(@id, 'report_template')]"

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Report Templates'
                and self.breadcrumb.read().startswith('Edit ')
        )

    @View.nested
    class template(SatTab):
        name = TextInput(id='report_template_name')
        default = Checkbox(id='report_template_default')
        template_editor = View.nested(TemplateEditor)
        audit = TextInput(id='report_template_audit_comment')

    @View.nested
    class type(SatTab):
        snippet = Checkbox(id='report_template_snippet')

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(
            id='ms-report_template_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(
            id='ms-report_template_organization_ids')


class ReportTemplateCreateView(TemplateCreateView, ReportTemplateDetailsView):

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Report Templates'
            and self.breadcrumb.read() == 'Create Template'
        )
