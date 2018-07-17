from widgetastic.widget import (
    Checkbox,
    ParametrizedLocator,
    Select,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import FilteredDropdown, SatTable


class MatcherAttribute(View):
    """Represent smart variable matcher attribute pair. Usually, it looks like
    as two fields separated by '=' mark
    """
    matcher_attribute_type = Select(
        ".//select[contains(@class, 'matcher_key')]")
    matcher_attribute_value = TextInput(
        locator=".//input[contains(@class, 'matcher_value')]")


class SmartVariableContent(View):
    ROOT = ParametrizedLocator('{@locator}')
    key = TextInput(locator=".//input[contains(@name, '[key]')]")
    description = TextInput(
        locator=".//textarea[contains(@name, '[description]')]")
    puppet_class = FilteredDropdown(id='variable_lookup_key_puppetclass_id')
    key_type = Select(locator=".//select[contains(@name, '[key_type]')]")
    default_value = TextInput(
        locator=".//textarea[contains(@name, '[default_value]')]")
    hidden = Checkbox(locator=".//input[contains(@name, '[hidden_value]')]")

    def __init__(self, parent, locator, logger=None):
        View.__init__(self, parent, logger=logger)
        self.locator = locator

    @View.nested
    class optional_input_validators(View):
        expander = Text(
            ".//h2[contains(@data-target, '#optional_input_validators_')]")
        validator_type = Select(
            locator=".//select[contains(@name, '[validator_type]')]")
        validator_rule = TextInput(
            locator=".//input[contains(@name, '[validator_rule]')]")

        def __init__(self, parent, logger=None):
            View.__init__(self, parent, logger=logger)
            if 'collapsed' in self.browser.element(
                    self.expander).get_attribute('class'):
                self.expander.click()
                self.browser.wait_for_element(
                    self.validator_type, visible=True)

    @View.nested
    class prioritize_attribute_order(View):
        order = TextInput(locator="//textarea[@id='order']")
        merge_overrides = Checkbox(
            locator=".//input[contains(@id, 'merge_overrides')]")
        merge_default = Checkbox(
            locator=".//input[contains(@id, 'merge_default')]")
        avoid_duplicates = Checkbox(
            locator=".//input[contains(@id, 'avoid_duplicates')]")

    @View.nested
    class matchers(View):
        table = SatTable(
            ".//table[contains(@class, 'white-header')]",
            column_widgets={
                'Attribute type': MatcherAttribute(),
                'Value': TextInput(
                    locator=".//textarea[contains(@id, 'value')]"),
            }
        )
        add_new_matcher = Text(
            ".//a[contains(@data-original-title, 'add a new matcher')]")

        def fill(self, values):
            """Example
            [
                {
                    'Attribute type': {
                        'matcher_attribute_type': 'os',
                        'matcher_attribute_value': 'x86'
                    },
                    'Value': 'newvalue'
                },
                {
                    'Attribute type': {
                        'matcher_attribute_type': 'fqdn',
                        'matcher_attribute_value': 'myhost.com'
                    },
                    'Value': 'newvalue2'
                }
            ]

            """
            for matcher_value in values:
                self.add_new_matcher.click()
                self.table[-1].fill(matcher_value)


class SmartVariablesTableView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Smart Variables']")
    new = Text("//a[contains(@href, '/variable_lookup_keys/new')]")
    table = SatTable(
        './/table',
        column_widgets={
            'Variable': Text('./a'),
            'Puppet Class': Text("./a[contains(@href, '/puppetclasses')]"),
            'Actions': Text('.//a[@data-method="delete"]'),
        }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class SmartVariableCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    variable = SmartVariableContent(locator="//div[@class='tab-pane fields']")
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Smart variables'
            and self.breadcrumb.read() == 'Create Smart Variable'
        )


class SmartVariableEditView(SmartVariableCreateView):

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Smart variables'
            and self.breadcrumb.read() == 'Edit Smart Variable'
        )
