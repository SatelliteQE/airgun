from widgetastic.widget import Checkbox
from widgetastic.widget import Select
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SatTable
from airgun.views.common import SearchableViewMixin
from airgun.widgets import CustomParameter
from airgun.widgets import FilteredDropdown
from airgun.widgets import Pagination
from airgun.widgets import SatSelect


class AnsibleVariablesView(BaseLoggedInView, SearchableViewMixin):
    """Main Ansible Variables view"""

    title = Text("//h1[contains(normalize-space(.),'Ansible Variables')]")
    new_variable = Text(
        "//a[contains(@href, '/ansible/ansible_variables/new')]")
    total_variables = Text(
        "//span[@class='pf-c-options-menu__toggle-text']//b[2]")
    table = SatTable(
        './/table',
        column_widgets={
            'Actions': Text(".//a[@data-method='delete']"),
        },
    )
    pagination = Pagination()

    @property
    def is_displayed(self):
        return self.title.is_displayed and self.new_variable.is_displayed


class MatcherTable(CustomParameter):
    add_new_value = Text("..//a[contains(text(),'+ Add Matcher')]")


class MatcherActions(View):
    """Interface table has Attribute type column that contains select field and
    text input field."""

    matcher_key = Select(".//select")
    matcher_value = TextInput(locator=".//input[@class='matcher_value']")


class NewAnsibleVariableView(BaseLoggedInView):
    """View while creating a new Ansible Variable"""

    breadcrumb = BreadCrumb()

    # 'Ansible Variable Details' section
    key = TextInput(id='ansible_variable_key')
    description = TextInput(id='ansible_variable_description')
    ansible_role = FilteredDropdown(id='ansible_variable_ansible_role_id')

    # 'Default Behavior' section
    override = Checkbox(id='ansible_variable_override')
    # Accessing all widgets except the ones above requires that the `override` checkbox is filled
    parameter_type = SatSelect(id='ansible_variable_parameter_type')
    default_value = TextInput(id='ansible_variable_default_value')
    hidden_value = Checkbox(id='ansible_variable_hidden_value')

    # 'Optional Input Validator' section
    expand_optional_input_validator = Text("//h2[@class='expander collapsed']")
    required = Checkbox(id='ansible_variable_required')
    validator_type = SatSelect(id='ansible_variable_validator_type')
    validator_rule = TextInput(id='ansible_variable_validator_rule')

    # 'Prioritize Attribute Order' section
    attribute_order = TextInput(id='order')
    merge_overrides = Checkbox(id='ansible_variable_merge_overrides')
    merge_default = Checkbox(id='ansible_variable_merge_default')
    avoid_duplicates = Checkbox(id='ansible_variable_avoid_duplicates')
    submit = Text('//input[@value="Submit"]')
    cancel = Text("//a[contains(., text()='Cancel']")

    @View.nested
    class matcher_section(View):
        """'Specify Matchers' section"""

        add_matcher = Text("//a[contains(@class, 'add_nested_fields')]")
        params = MatcherTable(
            locator=".//table[@class='table white-header']",
            # new_row_bottom is passed to the __init__ method of the
            # CustomParameter widget, see comment there for additional details
            new_row_bottom=True,
            column_widgets={
                'Attribute type': MatcherActions(),
                'Value': TextInput(locator=".//textarea[@id='new_lookup_value_value']"),
                'Actions': Text(".//a"),
            },
        )

        def before_fill(self, values):
            if not self.params.is_displayed:
                self.add_matcher.click()

    @property
    def expand_button(self):
        """Return the Optional Input Validator section expander element"""
        return self.browser.element(self.expand_optional_input_validator, parent=self)

    @property
    def expanded(self):
        """Check whether this section is expanded"""
        return 'active' in self.browser.get_attribute(
            'class', self.expand_optional_input_validator
        )

    def expand(self):
        """Expand the Optional Input Validator section"""
        if not self.expanded:
            self.browser.click(
                self.expand_optional_input_validator, parent=self)

    @property
    def is_displayed(self):
        return (
            self.breadcrumb.locations[0] == 'Ansible Variables'
            and self.breadcrumb.read() == 'Create Ansible Variable'
        )
