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
from airgun.widgets import SatTable, TextInputHidden


class MatcherAttribute(View):
    """Represent smart class parameter matcher attribute pair. Usually, it
    looks like as two fields separated by '=' mark
    """
    matcher_attribute_type = Select(
        ".//select[contains(@class, 'matcher_key')]")
    matcher_attribute_value = TextInput(
        locator=".//input[contains(@class, 'matcher_value')]")


class SmartClassParameterContent(View):
    ROOT = ParametrizedLocator('{@locator}')
    key = TextInput(locator=".//input[contains(@name, '[key]')]")
    description = TextInput(
        locator=".//textarea[contains(@name, '[description]')]")
    puppet_environment = TextInput(
        locator=".//input[contains(@name, '[environment_classes]')]")
    puppet_class = TextInput(
        locator=".//input[contains(@name, '[puppetclass_id]')]")
    override = Checkbox(
        locator=".//input[contains(@name, '[override]') and @type!='hidden']")
    parameter_type = Select(locator=".//select[contains(@name, '[parameter_type]')]")
    default_value = TextInputHidden(
        locator=".//textarea[contains(@name, '[default_value]')]")
    omit = Checkbox(
        locator=".//input[contains(@name, '[omit]') and @type!='hidden']")
    hidden = Checkbox(
        locator=".//input[contains(@name, '[hidden_value]') and "
                "@type!='hidden']"
    )

    def __init__(self, parent, locator, logger=None):
        View.__init__(self, parent, logger=logger)
        self.locator = locator

    @View.nested
    class optional_input_validators(View):
        expander = Text(
            ".//h2[contains(@data-target, '#optional_input_validators_')]")
        required = Checkbox(
            locator=".//input[contains(@name, '[required]') and "
                    "@type!='hidden']"
        )
        validator_type = Select(
            locator=".//select[contains(@name, '[validator_type]')]")
        validator_rule = TextInput(
            locator=".//input[contains(@name, '[validator_rule]')]")

        def __init__(self, parent, logger=None):
            View.__init__(self, parent, logger=logger)
            if 'collapsed' in self.browser.classes(self.expander):
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
                'Value': TextInputHidden(
                    locator=".//textarea[contains(@id, 'value')]"),
                'Omit': Checkbox(
                    locator=".//input[contains(@name, '[omit]') and "
                            "@type!='hidden']"
                )
            }
        )
        add_new_matcher = Text(
            ".//a[contains(@data-original-title, 'add a new matcher')]")

        def fill(self, values):
            """Add and fill all matchers provided
            Example::

                [
                    {
                        'Attribute type':
                        {
                            'matcher_attribute_type': 'os',
                            'matcher_attribute_value': 'x86'
                        },
                        'Value': 'newvalue'
                    },
                    {
                        'Attribute type':
                        {
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


class SmartClassParametersView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Smart Class Parameters']")
    table = SatTable(
        './/table',
        column_widgets={
            'Parameter': Text('./a'),
            'Puppet Class': Text("./a[contains(@href, '/puppetclasses')]"),
        }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class SmartClassParameterEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    parameter = SmartClassParameterContent(
        locator="//div[@class='tab-pane fields']")
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Smart Class Parameters'
            and len(self.breadcrumb.locations) == 2
        )
