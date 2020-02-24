from widgetastic.widget import ConditionalSwitchableView
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SatTab
from airgun.views.common import SearchableViewMixin
from airgun.views.dashboard import ItemValueList
from airgun.views.dashboard import TotalCount
from airgun.widgets import ActionsDropdown
from airgun.widgets import FilteredDropdown
from airgun.widgets import MultiSelect
from airgun.widgets import SatTable


class SCAPPoliciesView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Compliance Policies']")
    new = Text("//a[contains(@href, '/compliance/policies/new')]")
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


class SCAPPolicyCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    def fill(self, values):
        """overrides fill method, to be able to click next button during
        the creation process even, if no location or organization was selected,
        by adding the SCAP policy to Default Location or Organization."""
        if not values.get('organizations.resources.assigned'):
            values[
                'organizations.resources.assigned'] = ['Default Organization']

        if not values.get('locations.resources.assigned'):
            values['locations.resources.assigned'] = ['Default Location']
        super().fill(values)

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Policies'
            and self.breadcrumb.read() == 'New Compliance Policy'
        )

    @View.nested
    class create_policy(BaseLoggedInView):
        TAB_NAME = 'Create policy'
        next_step = Text("//input[contains(@value, 'Next')]")
        name = TextInput(id='policy_name')
        description = TextInput(id='policy_description')

        def after_fill(self, was_change):
            self.next_step.click()

    @View.nested
    class scap_content(BaseLoggedInView):
        TAB_NAME = 'SCAP Content'
        next_step = Text("//input[contains(@value, 'Next')]")
        scap_content_resource = FilteredDropdown(
            id='s2id_policy_scap_content_id')
        xccdf_profile = FilteredDropdown(
            id='s2id_policy_scap_content_profile_id')
        tailoring_file = FilteredDropdown(id='s2id_policy_tailoring_file_id')
        xccdf_profile_tailoring_file = FilteredDropdown(
            id='s2id_policy_tailoring_file_profile_id')

        def after_fill(self, was_change):
            self.next_step.click()

    @View.nested
    class schedule(BaseLoggedInView):
        next_step = Text("//input[contains(@value, 'Next')]")
        period = FilteredDropdown(id='s2id_policy_period')
        period_selection = ConditionalSwitchableView(reference='period')

        @period_selection.register('Weekly')
        class WeeklyPeriodForm(View):
            weekday = FilteredDropdown(id='s2id_policy_weekday')

        @period_selection.register('Monthly')
        class MonthlyPeriodForm(View):
            day_of_month = FilteredDropdown(id='s2id_policy_day_of_month')

        @period_selection.register('Custom')
        class CustomPeriodForm(View):
            cron_line = TextInput(id='policy_cron_line')

        def after_fill(self, was_change):
            self.next_step.click()

    @View.nested
    class locations(BaseLoggedInView):
        next_step = Text("//input[contains(@value, 'Next')]")
        resources = MultiSelect(id='ms-policy_location_ids')

        def after_fill(self, was_change):
            self.next_step.click()

    @View.nested
    class organizations(BaseLoggedInView):
        next_step = Text("//input[contains(@value, 'Next')]")
        resources = MultiSelect(id='ms-policy_organization_ids')

        def after_fill(self, was_change):
            self.next_step.click()

    @View.nested
    class host_group(BaseLoggedInView):
        TAB_NAME = 'Host Groups'
        submit = Text('//input[@name="commit"]')
        resources = MultiSelect(id='ms-policy_hostgroup_ids')


class SCAPPolicyEditView(BaseLoggedInView):
    submit = Text('//input[@name="commit"]')
    cancel = Text("//a[text()='Cancel']")
    breadcrumb = BreadCrumb()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Policies'
            and self.breadcrumb.read() != 'New Compliance Policy'
        )

    @View.nested
    class general(SatTab):
        name = TextInput(id='policy_name')
        description = Text('//textarea[@id="policy_description"]')

    @View.nested
    class scap_content(SatTab):
        TAB_NAME = 'SCAP Content'
        scap_content = FilteredDropdown(id='s2id_policy_scap_content_id')
        xccdf_profile = FilteredDropdown(
            id='s2id_policy_scap_content_profile_id')
        tailoring_file = FilteredDropdown(id='s2id_policy_tailoring_file_id')
        xccdf_profile_tailoring_file = FilteredDropdown(
            id='s2id_policy_tailoring_file_profile_id')

    @View.nested
    class schedule(SatTab):
        period = FilteredDropdown(id='s2id_policy_period')
        period_selection = ConditionalSwitchableView(reference='period')

        @period_selection.register('Weekly')
        class WeeklyPeriodForm(View):
            weekday = FilteredDropdown(id='s2id_policy_weekday')

        @period_selection.register('Monthly')
        class MonthlyPeriodForm(View):
            day_of_month = FilteredDropdown(id='s2id_policy_day_of_month')

        @period_selection.register('Custom')
        class CustomPeriodForm(View):
            cron_line = TextInput(id='policy_cron_line')

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(id='ms-policy_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(id='ms-policy_organization_ids')

    @View.nested
    class host_group(SatTab):
        TAB_NAME = 'Host Groups'
        resources = MultiSelect(id='ms-policy_hostgroup_ids')


class SCAPPolicyDetailsView(BaseLoggedInView):
    title = Text('h1[text()[contains(., "Compliance policy")]]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None

    @View.nested
    class HostsBreakdownStatus(View):
        ROOT = ".//li[@data-name='Status table']"
        status_list = ItemValueList()
        total_count = TotalCount()

    @View.nested
    class HostBreakdownChart(View):
        """Refer to information from the middle of the chart in Oscap Policy
        Details View
        """
        hosts_breakdown = Text('//div[@id="overview"]/span[@id="pieLabel3"]')
