from wait_for import wait_for
from widgetastic.widget import Checkbox, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly4 import Button, DescriptionList, Radio, Select
from widgetastic_patternfly4.donutchart import DonutCircle, DonutLegend
from widgetastic_patternfly4.ouia import (
    Dropdown as OUIADropdown,
    Select as OUIASelect,
    Text as OUIAText,
)
from widgetastic_patternfly5 import (
    ChipGroup as PF5ChipGroup,
)
from widgetastic_patternfly5.ouia import (
    Select as PF5OUIASelect,
)

from airgun.views.common import (
    BaseLoggedInView,
    SatTab,
    SatTable,
    SearchableViewMixin,
    WizardStepView,
)
from airgun.widgets import ActionsDropdown, ExpandableSection, PF4DataList


class JobInvocationsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[contains(., 'Job') and contains(., 'nvocations')]")
    new = Text("//a[contains(@href, '/job_invocations/new')]")
    table = SatTable('.//table', column_widgets={'Description': Text('./a')})

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class JobInvocationCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    @View.nested
    class category_and_template(WizardStepView):
        expander = Text(".//button[contains(.,'Category and template')]")
        job_category = PF5OUIASelect('job_category')
        job_template = PF5OUIASelect('job_template')
        job_template_text_input = TextInput(
            locator='//div[contains(@class, "pf-v5-c-form__group") and .//label[.//span[text()="Job template"]]]//input[@type="text"]'
        )

    @View.nested
    class target_hosts_and_inputs(WizardStepView):
        expander = Text(".//button[contains(.,'Target hosts and inputs')]")
        command = TextInput(id='command')

        selected_hosts = PF5ChipGroup(locator='//div[@class="selected-chips"]/div')

        package_action = OUIASelect('OUIA-Generated-Select-single-15')
        package = TextInput(id='package')

        action = Select(locator='//div[button[@aria-label="action toggle"]]')
        service = TextInput(id='service')

        module_action = OUIASelect('OUIA-Generated-Select-single-31')
        module_spec = TextInput(id='module_spec')
        options = TextInput(id='options')

        ansible_collections_list = TextInput(id='ansible_collections_list')
        ansible_roles_list = TextInput(id='ansible_roles_list')
        power_action = OUIASelect('OUIA-Generated-Select-single-34')

        targetting_type = Select(locator='//div[button[@aria-haspopup="listbox"]]')
        targets = Select(locator='//div[contains(@data-ouia-component-id,"hosts")]')

    @View.nested
    class advanced_fields(WizardStepView):
        expander = Text(".//button[contains(.,'Advanced fields')]")
        ssh_user = TextInput(id='ssh-user')
        effective_user = TextInput(id='effective-user')
        timeout_to_kill = TextInput(id='timeout-to-kill')
        time_to_pickup = TextInput(id='time-to-pickup')
        password = TextInput(id='job-password')
        pk_passphrase = TextInput(id='key-passphrase')
        effective_user_password = TextInput(id='effective-user-password')
        concurrency_level = TextInput(id='concurrency-level')
        time_span = TextInput(id='time-span')
        execution_order_alphabetical = Radio(id='execution-order-alphabetical')
        execution_order_randomized = Radio(id='execution-order-randomized')
        ansible_collections_path = TextInput(id='collections_path')

    @View.nested
    class schedule(WizardStepView):
        expander = Text(".//button[contains(.,'Type of execution')]")
        # Execution type
        immediate = Radio(id='schedule-type-now')
        future = Radio(id='schedule-type-future')
        recurring = Radio(id='schedule-type-recurring')
        # Query type
        static_query = Radio(id='query-type-static')
        dynamic_query = Radio(id='query-type-dynamic')

    @View.nested
    class schedule_future_execution(WizardStepView):
        expander = Text(".//button[contains(.,'Future execution')]")
        start_at_date = TextInput(locator='//input[contains(@aria-label, "starts at datepicker")]')
        start_at_time = TextInput(locator='//input[contains(@aria-label, "starts at timepicker")]')
        start_before_date = TextInput(
            locator='//input[contains(@aria-label, "starts before datepicker")]'
        )
        start_before_time = TextInput(
            locator='//input[contains(@aria-label, "starts before timepicker")]'
        )

    @View.nested
    class schedule_recurring_execution(WizardStepView):
        expander = Text(".//button[contains(.,'Recurring execution')]")
        # Starts
        start_now = Radio(id='start-now')
        start_at = Radio(id='start-at')
        start_at_date = TextInput(locator='//input[contains(@aria-label, "starts at datepicker")]')
        start_at_time = TextInput(locator='//input[contains(@aria-label, "starts at timepicker")]')
        # Repeats
        repeats = OUIASelect('OUIA-Generated-Select-single-3')
        repeats_at = TextInput(locator='//input[contains(@aria-label, "repeat-at")]')
        # Ends
        ends_never = Radio(id='never-ends')
        ends_on = Radio(id='ends-on')
        ends_on_date = TextInput(locator='//input[contains(@aria-label, "ends on datepicker")]')
        ends_on_time = TextInput(locator='//input[contains(@aria-label, "ends on timepicker")]')
        ends_after = Radio(id='ends-after')
        ends_after_count = TextInput(locator='//input[contains(@id, "repeat-amount")]')
        purpose = TextInput(locator='//input[contains(@aria-label, "purpose")]')

    @View.nested
    class submit(WizardStepView):
        expander = Text(".//button[contains(.,'Review')]")
        submit = Text(".//button[contains(.,'Submit')]")

        def click(self):
            self.submit.click()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Jobs'
            and self.breadcrumb.read() == 'Job invocation'
        )


class JobInvocationStatusView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    BREADCRUMB_LENGTH = 2

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Jobs'
            and len(self.breadcrumb.locations) == self.BREADCRUMB_LENGTH
        )

    rerun = Text("//a[normalize-space(.)='Rerun']")
    rerun_failed = Text("//a[normalize-space(.)='Rerun failed']")
    job_task = Text("//a[normalize-space(.)='Job Task']")
    cancel_job = Button(value='Cancel Job')
    abort_job = Button(value='Abort Job')
    new_ui = Text("//a[normalize-space(.)='New UI']")

    @View.nested
    class overview(SatTab):
        job_status = Text(
            "//div[@id='job_invocations_chart_container']"
            "//*[name()='tspan'][contains(@class,'donut-title-small-pf')]"
        )
        job_status_progress = Text(
            "//div[@id='job_invocations_chart_container']"
            "//*[name()='tspan'][contains(@class,'donut-title-big-pf')]"
        )
        execution_order = Text("//p[contains(., 'Execution order:')]")
        hosts_table = SatTable(
            './/table',
            column_widgets={
                'Host': Text('./a'),
                'Actions': ActionsDropdown('.//div[contains(@class, "btn-group")]'),
            },
        )
        total_hosts = Text(
            "//h2[contains(., 'Total hosts')]/span[@class='card-pf-aggregate-status-count']"
        )

    @View.nested
    class leapp_preupgrade_report(SatTab):
        ROOT = '//div[@id="content"]//ul/li/a[contains(text(), "Leapp preupgrade report")][@href="#leapp_preupgrade_report"]'
        TAB_NAME = 'Leapp preupgrade report'

        leapp_report_title = Checkbox(
            locator='//*[@id="preupgrade-report-entries-list-view"]//input[@type="checkbox"]'
        )
        fix_selected = Text('//*[@id="leapp_preupgrade_report"]//button[text()="Fix Selected"]')
        run_upgrade = Text('//*[@id="leapp_preupgrade_report"]//button[text()="Run Upgrade"]')

    def wait_for_result(self, timeout=600, delay=1):
        """Wait for invocation job to finish"""
        wait_for(
            lambda: (
                self.is_displayed
                and self.overview.job_status.is_displayed
                and self.overview.job_status_progress.is_displayed
            ),
            timeout=timeout,
            delay=delay,
            logger=self.logger,
        )
        wait_for(
            lambda: (
                self.overview.job_status.read() != 'Pending'
                and self.overview.job_status_progress.read() == '100%'
            ),
            timeout=timeout,
            delay=1,
            logger=self.logger,
        )


class NewJobInvocationStatusView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    title = OUIAText('breadcrumb_title')
    create_report = Button(value='Create report')
    actions = OUIADropdown('job-invocation-global-actions-dropdown')
    BREADCRUMB_LENGTH = 2

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.breadcrumb.wait_displayed()
        title_loaded = self.title.wait_displayed()
        data_loaded, _ = wait_for(
            func=lambda: self.status.is_displayed,
            timeout=60,
            delay=15,
            fail_func=self.browser.refresh,
        )
        return (
            breadcrumb_loaded
            and title_loaded
            and data_loaded
            and self.breadcrumb.locations[0] == 'Jobs'
            and len(self.breadcrumb.locations) == self.BREADCRUMB_LENGTH
        )

    @View.nested
    class overall_status(DonutCircle):
        """The donut circle with the overall job status of '{succeeded hosts}/{total hosts}'"""

        def read(self):
            """Return `dict` with the parsed overall status numbers, for example:
            ```{'succeeded_hosts': 2, 'total_hosts': 5}```
            """
            succeeded_hosts, total_hosts = self.labels[0].split('/')
            return {'succeeded_hosts': int(succeeded_hosts), 'total_hosts': int(total_hosts)}

    @View.nested
    class status(DonutLegend):
        """'System status' panel."""

        ROOT = ".//div[contains(@class, 'chart-legend')]"
        first_label = Text(locator="//*[@id='legend-labels-0']")

        @property
        def is_displayed(self):
            """Any status label is displayed after all data are loaded."""
            return self.first_label.is_displayed

        def read(self):
            """Return `dict` with the System status info.
            Example: ```{'Succeeded': 2, 'Failed': 1, 'In Progress': 0, 'Canceled': 0}```
            """
            return {item['label']: int(item['value']) for item in self.all_items}

    @View.nested
    class overview(DescriptionList):
        ROOT = ".//div[contains(@class, 'job-overview')]"

        def read(self):
            """Return `dict` without trailing ':' in the key names."""
            return {key.replace(':', ''): val for key, val in super().read().items()}

    @View.nested
    class target_hosts(ExpandableSection):
        label = 'Target Hosts'
        search_query = Text('./div[contains(@class, "pf-c-expandable-section__content")]/pre')
        data = PF4DataList()

        def read(self):
            return {'search_query': self.search_query.read(), 'data': self.data.read()}

    @View.nested
    class user_inputs(ExpandableSection):
        label = 'User Inputs'
        data = PF4DataList()

        def read(self):
            return {'data': self.data.read()}
