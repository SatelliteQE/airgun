from widgetastic.widget import Checkbox, Select, Table, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import (
    BaseLoggedInView,
    SatTab,
    SearchableViewMixin,
    TemplateEditor,
    TemplateInputItem,
)
from airgun.widgets import (
    ActionsDropdown,
    FilteredDropdown,
    GenericRemovableWidgetItem,
    MultiSelect,
    RemovableWidgetsItemsListView,
)


class JobTemplatesView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[contains(., 'Job Templates')]")
    import_template = Text("//a[normalize-space(.)='Import']")
    new = Text("//a[contains(@href, '/job_templates/new')]")
    table = Table(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        },
    )

    @property
    def is_displayed(self):
        return self.title.is_displayed


class JobTemplateForeignInputSetItem(GenericRemovableWidgetItem):
    """Job Template Foreign Input Set Item widget"""

    remove_button = Text(".//a[contains(@class, 'remove_nested_fields')]")
    target_template = Select(locator=".//select[contains(@name, '[target_template_id]')]")
    include_all = Checkbox(locator=".//input[contains(@id, 'include_all')]")
    include = TextInput(locator=".//input[contains(@name, '[include]')]")
    exclude = TextInput(locator=".//input[contains(@name, '[exclude]')]")


class JobTemplateCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'Job Templates'
            and self.breadcrumb.read() == 'New Job Template'
        )

    @View.nested
    class template(SatTab):
        name = TextInput(id='job_template_name')
        default = Checkbox(id='job_template_default')
        template_editor = View.nested(TemplateEditor)
        description = TextInput(id='job_template_description')
        audit = TextInput(id='job_template_audit_comment')

    @View.nested
    class inputs(RemovableWidgetsItemsListView, SatTab):
        ITEMS = ".//div[contains(@class, 'template_inputs')]/following-sibling::div"
        ITEM_WIDGET_CLASS = TemplateInputItem
        add_item_button = Text(".//a[@data-association='template_inputs']")

    @View.nested
    class job(SatTab):
        job_category = TextInput(name='job_template[job_category]')
        description_format = TextInput(id='job_template_description_format')
        provider_type = FilteredDropdown(id='job_template_provider_type')
        timeout = TextInput(id='job_template_execution_timeout_interval')

        @View.nested
        class foreign_input_sets(RemovableWidgetsItemsListView):
            ROOT = "//div[div[contains(@class, 'foreign_input_sets')]]"
            ITEMS = ".//div[contains(@class, 'foreign_input_sets')]/following-sibling::div"
            ITEM_WIDGET_CLASS = JobTemplateForeignInputSetItem
            add_item_button = Text(".//a[@data-association='foreign_input_sets']")

        value = TextInput(id='job_template_effective_user_attributes_value')
        current_user = Checkbox(id='job_template_effective_user_attributes_current_user')
        overridable = Checkbox(id='job_template_effective_user_attributes_overridable')

    @View.nested
    class type(SatTab):
        snippet = Checkbox(id='job_template_snippet')

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(id='ms-job_template_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(id='ms-job_template_organization_ids')


class JobTemplateEditView(JobTemplateCreateView):
    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'Job Templates'
            and self.breadcrumb.read().startswith('Edit ')
        )
