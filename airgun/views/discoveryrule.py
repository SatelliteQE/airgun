from widgetastic.widget import (
    Checkbox,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb

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
    submit = Text('//input[@name="commit"]')
    cancel = Text('//a[text()="Cancel"]')
    breadcrumb = BreadCrumb()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Discovery rules'
                and self.breadcrumb.read() == 'New Discovery Rule'
        )

    @View.nested
    class primary(SatTab):
        name = TextInput(id='discovery_rule_name')
        search = TextInput(id='search')
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
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Discovery rules'
            and self.breadcrumb.read().startswith('Edit ')
        )
