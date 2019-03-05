from widgetastic.widget import (
        Checkbox,
        ConditionalSwitchableView,
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
)
from airgun.widgets import (
    ActionsDropdown,
    GenericRemovableWidgetItem,
    RemovableWidgetsItemsListView,
    SatSelect,
)


class TemplateInputItem(GenericRemovableWidgetItem):
    """Report Template Input item widget"""
    remove_button = Text(".//a[@class='remove_nested_fields']")
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


class TemplatesView(BaseLoggedInView, SearchableViewMixin):
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


class TemplateDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @View.nested
    class inputs(RemovableWidgetsItemsListView, SatTab):
        ITEMS = ".//div[contains(@class, 'template_inputs')]/following-sibling::div"
        ITEM_WIDGET_CLASS = TemplateInputItem
        add_item_button = Text(".//a[@data-association='template_inputs']")
        snippet = Checkbox(id='report_template_snippet')


class TemplateCreateView(TemplateDetailsView):
    pass
