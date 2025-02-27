from widgetastic.widget import Checkbox, Table, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb, Button

from airgun.views.common import (
    BaseLoggedInView,
    SatTab,
    SearchableViewMixinPF4,
    TemplateEditor,
    TemplateInputItem,
)
from airgun.widgets import (
    ActionsDropdown,
    FilteredDropdown,
    MultiSelect,
    RemovableWidgetsItemsListView,
    TextInputsGroup,
)


class ReportTemplatesView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[normalize-space(.)='Report Templates']")
    new = Button("Create Template")
    table = Table(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Locked': Text('.'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ReportTemplateDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
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
    class inputs(RemovableWidgetsItemsListView, SatTab):
        ITEMS = ".//div[contains(@class, 'template_inputs')]/following-sibling::div"
        ITEM_WIDGET_CLASS = TemplateInputItem
        add_item_button = Text(".//a[@data-association='template_inputs']")

    @View.nested
    class type(SatTab):
        snippet = Checkbox(id='report_template_snippet')

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(id='ms-report_template_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(id='ms-report_template_organization_ids')


class ReportTemplateCreateView(ReportTemplateDetailsView):
    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Report Templates'
            and self.breadcrumb.read() == 'Create Template'
        )


class ReportTemplateGenerateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    email = Checkbox(id='report_template_report_send_mail')
    email_to = TextInput(id='report_template_report_mail_to')
    inputs = TextInputsGroup(locator='.//form')
    output_format = FilteredDropdown(id='report_template_report_format')
    hosts_filter = TextInput(locator='//input[contains(@class,"search-input")]')
    generate_at = TextInput(id='report_template_report_generate_at')
    submit = Text('//input[@name="commit"]')
    generated = Text('//div[contains(@class, "alert-success")]')
    installability = FilteredDropdown(id='Installability')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Report Templates'
            and self.breadcrumb.read() == 'Generate a Report'
        )
