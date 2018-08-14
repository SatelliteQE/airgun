from widgetastic.widget import (
    Checkbox,
    ConditionalSwitchableView,
    Select,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import (
    BaseLoggedInView,
    SatTab,
    SatTable,
    SearchableViewMixin,
    TemplateEditor,
)
from airgun.widgets import (
    ActionsDropdown,
    FilteredDropdown,
    MultiSelect,
    SatSelect,
)


class JobTemplatesView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[contains(., 'Job Templates')]")
    import_template = Text("//a[text()='Import']")
    new = Text("//a[contains(@href, '/job_templates/new')]")
    table = SatTable(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class JobTemplateCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Templates'
            and self.breadcrumb.read() == 'New Job Template'
        )

    @View.nested
    class template(SatTab):
        name = TextInput(id='job_template_name')
        default = Checkbox(id='job_template_default')
        template_editor = View.nested(TemplateEditor)
        audit = TextInput(id='job_template_audit_comment')

    @View.nested
    class job(SatTab):
        job_category = TextInput(name='job_template[job_category]')
        description_format = TextInput(id='job_template_description_format')
        provider_type = FilteredDropdown(id='job_template_provider_type')
        timeout = TextInput(id='job_template_execution_timeout_interval')
        add_template_inputs = Text("//a[@data-association='template_inputs']")
        add_foreign_input_set = Text(
            "//a[@data-association='foreign_input_sets']")

        @View.nested
        class template_input(View):
            ROOT = "//div[contains(@class, 'template_inputs')]" \
                   "/following-sibling::div[1]"
            name = TextInput(locator=".//input[contains(@name, '[name]')]")
            required = Checkbox(locator=".//input[contains(@id, 'required')]")
            input_type = SatSelect(
                locator=".//select[contains(@name, '[input_type]')]")

            input_content = ConditionalSwitchableView(reference='input_type')

            @input_content.register('User input')
            class UserInputForm(View):
                advanced = Checkbox(
                    locator=".//input[contains(@id, 'advanced')]")
                options = TextInput(
                    locator=".//textarea[contains(@name, '[options]')]")
                description = TextInput(
                    locator=".//textarea[contains(@name, '[description]')]")

            @input_content.register('Fact value')
            class FactValueForm(View):
                fact_name = TextInput(
                    locator=".//input[contains(@name, '[fact_name]')]")
                description = TextInput(
                    locator=".//textarea[contains(@name, '[description]')]")

            @input_content.register('Variable value')
            class VariableValueForm(View):
                variable_name = TextInput(
                    locator=".//input[contains(@name, '[variable_name]')]")
                description = TextInput(
                    locator=".//textarea[contains(@name, '[description]')]")

            @input_content.register('Puppet parameter')
            class PuppetParameterForm(View):
                puppet_class_name = TextInput(
                    locator=".//input[contains(@name, '[puppet_class_name]')]")
                puppet_parameter_name = TextInput(
                    locator=".//input[contains("
                            "@name, '[puppet_parameter_name]')]")
                description = TextInput(
                    locator=".//textarea[contains(@name, '[description]')]")

            def before_fill(self, values=None):
                self.parent.add_template_inputs.click()

        @View.nested
        class foreign_input(View):
            ROOT = "//div[contains(@class, 'foreign_input')]" \
                   "/following-sibling::div[1]"
            target_template = Select(
                locator=".//select[contains(@name, '[target_template_id]')]")
            include_all = Checkbox(
                locator=".//input[contains(@id, 'include_all')]")
            include = TextInput(
                locator=".//input[contains(@name, '[include]')]")
            exclude = TextInput(
                locator=".//input[contains(@name, '[exclude]')]")

            def before_fill(self, values=None):
                self.parent.add_foreign_input_set.click()

        value = TextInput(
            id='job_template_effective_user_attributes_value')
        current_user = Checkbox(
            id='job_template_effective_user_attributes_current_user')
        overridable = Checkbox(
            id='job_template_effective_user_attributes_overridable')

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
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Job Templates'
            and self.breadcrumb.read().startswith('Edit ')
        )
