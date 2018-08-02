from widgetastic.widget import (
    Checkbox,
    Text,
    TextInput,
    View,
)

from airgun.views.common import (
    BaseLoggedInView,
    SatTab,
    SearchableViewMixin,
)
from airgun.widgets import (
    ActionsDropdown,
    FilteredDropdown,
    MultiSelect,
    SatTable,
)


class DiscoveryRulesView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Discovery Rules']")
    new = Text("//a[contains(@href, '/discovery_rules/new')]")
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


class DiscoveryRuleCreateView(BaseLoggedInView):
    name = TextInput(locator="//input[@id='discovery_rule_name']")
    search = TextInput(locator="//input[@id='search']")
    host_group = FilteredDropdown(id='discovery_rule_hostgroup_id')
    hostname = TextInput(id='discovery_rule_hostname')
    hosts_limit = TextInput(id='discovery_rule_max_count')
    priority = TextInput(id='discovery_rule_priority')
    enabled = Checkbox(id='discovery_rule_enabled')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None


class DiscoveryRuleEditView(BaseLoggedInView):
    name = TextInput(locator="//input[@id='discovery_rule_name']")
    search = TextInput(locator="//input[@id='search']")
    host_group = FilteredDropdown(id='discovery_rule_hostgroup_id')
    hostname = TextInput(id='discovery_rule_hostname')
    hosts_limit = TextInput(id='discovery_rule_max_count')
    priority = TextInput(id='discovery_rule_priority')
    enabled = Checkbox(id='discovery_rule_enabled')
    submit = Text("//input[@name='commit']")
    cancel = Text("//a[text()='Cancel']")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(id='ms-discovery_rule_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(id='ms-discovery_rule_organization_ids')
