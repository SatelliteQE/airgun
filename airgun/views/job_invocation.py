from wait_for import wait_for
from widgetastic.widget import Text, TextInput, View
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly4 import Button, Radio
from widgetastic_patternfly4.ouia import Select

from airgun.views.common import (
    BaseLoggedInView,
    SatTab,
    SatTable,
    SearchableViewMixin,
    WizardStepView,
)
from airgun.widgets import ActionsDropdown


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
        job_category = Select('OUIA-Generated-Select-single-1')
        job_template = Select('OUIA-Generated-Select-typeahead-1')

    @View.nested
    class target_hosts_and_inputs(WizardStepView):
        expander = Text(".//button[contains(.,'Target hosts and inputs')]")
        command = TextInput(id='command')

        package_action = Select('OUIA-Generated-Select-single-15')
        package = TextInput(id='package')

        service_action = Select('OUIA-Generated-Select-single-28')
        service = TextInput(id='service')

        module_action = Select('OUIA-Generated-Select-single-31')
        module_spec = TextInput(id='module_spec')
        options = TextInput(id='options')

        power_action = Select('OUIA-Generated-Select-single-34')

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
        repeats = Select('OUIA-Generated-Select-single-3')
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
        submit = Text(".//button[contains(.,'Run')]")

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
                'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
            },
        )
        total_hosts = Text(
            "//h2[contains(., 'Total hosts')]/span[@class='card-pf-aggregate-status-count']"
        )

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
