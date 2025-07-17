from widgetastic.widget import Checkbox, Table, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly5 import Button as PF5Button

from airgun.views.common import BaseLoggedInView, SatTab, SearchableViewMixinPF4
from airgun.widgets import (
    ActionsDropdown,
    AutoCompleteTextInput,
    FilteredDropdown,
    MultiSelect,
)


class DiscoveryRulesView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[normalize-space(.)='Discovery Rules']")
    page_info = Text("//foreman-react-component[contains(@name, 'DiscoveryRules')]/div/div")
    new = Text("//a[contains(@href, '/discovery_rules/new')]")
    new_on_blank_page = PF5Button('Create Rule')
    table = Table(
        './/table',
        column_widgets={
            'Name': Text('.//a'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class DiscoveryRuleCreateView(BaseLoggedInView):
    submit = Text('//input[@name="commit"]')
    cancel = Text('//a[normalize-space(.)="Cancel"]')
    breadcrumb = BreadCrumb()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Discovery rules'
            and self.breadcrumb.read() == 'New Discovery Rule'
        )

    @View.nested
    class primary(SatTab):
        name = TextInput(id='discovery_rule_name')
        search = AutoCompleteTextInput(name='discovery_rule[search]')
        host_group = FilteredDropdown(id='discovery_rule_hostgroup_id')
        hostname = TextInput(id='discovery_rule_hostname')
        hosts_limit = TextInput(id='discovery_rule_max_count')
        priority = TextInput(id='discovery_rule_priority')
        enabled = Checkbox(id='discovery_rule_enabled')

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(id='ms-discovery_rule_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(id='ms-discovery_rule_organization_ids')


class DiscoveryRuleEditView(DiscoveryRuleCreateView):
    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Discovery rules'
            and self.breadcrumb.read().startswith('Edit ')
        )
