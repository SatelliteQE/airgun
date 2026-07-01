from time import sleep

from selenium.common.exceptions import NoSuchElementException
from wait_for import TimedOutError, wait_for
from widgetastic.widget import Checkbox, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly5 import (
    ChipGroup as PF5ChipGroup,
    DescriptionList,
    Radio as PF5Radio,
)
from widgetastic_patternfly5.charts.donut_chart import DonutCircle, DonutLegend
from widgetastic_patternfly5.ouia import (
    Button as PF5OUIAButton,
    Dropdown as PF5OUIADropdown,
    ExpandableTable as PF5OUIAExpandableTable,
    Select as PF5OUIASelect,
    Text as PF5OUIAText,
    TextInput as PF5OUIATextInput,
)

from airgun.views.common import (
    BaseLoggedInView,
    PF5WizardStepView,
    SatTable,
    SearchableViewMixin,
)
from airgun.widgets import PF5DataList, PF5LabeledExpandableSection


class HostsExpandableTable(PF5OUIAExpandableTable):
    def read(self):
        """Reads the hosts table.
        For some reason, the hosts expandable table has always an extra empty <tbody/> tag at the end.
        This causes problems for the table parser to process it properly.
        So far, the only way to fix it seems to be manually removing the extra tag from the page.

        Note: `silent_failure=True` in the second `wait_for` function ensures the JavaScript
        execution does not time out in case the hosts table is empty.
        Then `super().read()` should return empty list.
        """
        wait_for(func=lambda: self.is_displayed, timeout=15, delay=1)
        self.browser.plugin.ensure_page_safe(timeout=15)
        script = f"""
        rows = document.getElementsByTagName('{self.ROW_TAG}');
        last_row = rows[rows.length-1];
        if (last_row.innerText.trim() === '') {{
            last_row.remove();
            return true;
        }} else {{
            return false;
        }}
        """
        wait_for(
            func=lambda: self.browser.execute_script(script),
            timeout=15,
            delay=1,
            silent_failure=True,
        )
        return super().read()


class JobInvocationsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[contains(., 'Job') and contains(., 'nvocations')]")
    new = Text("//a[contains(@href, '/job_invocations/new')]")
    table = SatTable('.//table', column_widgets={'Description': Text('./a')})

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class JobInvocationCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    # PF5 Wizard footer buttons
    next_button = PF5OUIAButton(component_id='next-footer')
    back_button = PF5OUIAButton(component_id='back-footer')
    run_on_selected = PF5OUIAButton(component_id='run-on-selected-hosts-footer')
    skip_to_review = PF5OUIAButton(component_id='skip-to-review-footer')
    cancel_button = PF5OUIAButton(component_id='cancel-footer')
    # Note: submit button might have different ID or only appear on review step
    submit_button = Text(
        ".//button[contains(., 'Submit') or @data-ouia-component-id='submit-footer']"
    )

    @View.nested
    class category_and_template(PF5WizardStepView):
        job_category = PF5OUIASelect('job_category')
        job_template = PF5OUIASelect('job_template')
        job_template_text_input = TextInput(
            locator='//div[contains(@class, "pf-v5-c-form__group") and .//label[.//span[text()="Job template"]]]//input[@type="text"]'
        )

    @View.nested
    class target_hosts_and_inputs(PF5WizardStepView):
        command = TextInput(id='command')

        selected_hosts = PF5ChipGroup(locator='//div[@class="selected-chips"]/div')

        package_action = PF5OUIASelect('action')
        package = TextInput(id='package')

        action = PF5OUIASelect('action')
        service = TextInput(id='service')

        module_action = PF5OUIASelect('action')
        module_spec = TextInput(id='module_spec')
        options = TextInput(id='options')

        ansible_collections_list = TextInput(id='ansible_collections_list')
        ansible_roles_list = TextInput(id='ansible_roles_list')
        power_action = PF5OUIASelect('action')

        targetting_type = PF5OUIASelect('host_methods')
        targets = PF5OUIASelect('hosts')
        targets_host_groups = PF5OUIASelect('host groups')
        targets_host_collecitons = PF5OUIASelect('host collections')

    @View.nested
    class advanced_fields(PF5WizardStepView):
        ssh_user = PF5OUIATextInput('ssh-user')
        effective_user = PF5OUIATextInput('effective-user')
        timeout_to_kill = PF5OUIATextInput('timeout-to-kill')
        time_to_pickup = PF5OUIATextInput('time-to-pickup')
        password = PF5OUIATextInput('job-password')
        pk_passphrase = PF5OUIATextInput('key-passphrase')
        effective_user_password = PF5OUIATextInput('effective-user-password')
        concurrency_level = PF5OUIATextInput('concurrency-level')
        time_span = PF5OUIATextInput('time-span')
        execution_order_alphabetical = PF5Radio(id='execution-order-alphabetical')
        execution_order_randomized = PF5Radio(id='execution-order-randomized')
        ansible_collections_path = TextInput(id='collections_path')

    @View.nested
    class schedule(PF5WizardStepView):
        # Execution type
        immediate = PF5Radio(id='schedule-type-now')
        future = PF5Radio(id='schedule-type-future')
        recurring = PF5Radio(id='schedule-type-recurring')
        # Query type
        static_query = PF5Radio(id='query-type-static')
        dynamic_query = PF5Radio(id='query-type-dynamic')

    @View.nested
    class schedule_future_execution(PF5WizardStepView):
        start_at_date = TextInput(locator='//input[contains(@aria-label, "starts at datepicker")]')
        start_at_time = TextInput(locator='//input[contains(@aria-label, "starts at timepicker")]')
        start_before_date = TextInput(
            locator='//input[contains(@aria-label, "starts before datepicker")]'
        )
        start_before_time = TextInput(
            locator='//input[contains(@aria-label, "starts before timepicker")]'
        )

    @View.nested
    class schedule_recurring_execution(PF5WizardStepView):
        # Starts
        start_now = PF5Radio(id='start-now')
        start_at = PF5Radio(id='start-at')
        start_at_date = TextInput(locator='//input[contains(@aria-label, "starts at datepicker")]')
        start_at_time = TextInput(locator='//input[contains(@aria-label, "starts at timepicker")]')
        # Repeats
        repeats = PF5OUIASelect('repeat-select')
        repeats_at = TextInput(locator='//input[contains(@aria-label, "repeat-at")]')
        # Ends
        ends_never = PF5Radio(id='schedule-never-ends')
        ends_on = PF5Radio(id='schedule-ends-on-date')
        ends_on_date = TextInput(locator='//input[contains(@aria-label, "ends on datepicker")]')
        ends_on_time = TextInput(locator='//input[contains(@aria-label, "ends on timepicker")]')
        ends_after = PF5Radio(id='schedule-ends-after')
        ends_after_count = TextInput(locator='//input[contains(@id, "repeat-amount")]')
        purpose = TextInput(locator='//input[contains(@aria-label, "purpose")]')

    # Note: The submit button is in the wizard footer
    # Keep this class for backward compatibility
    @View.nested
    class submit(PF5WizardStepView):
        # The actual submit button locator
        submit = Text(".//button[contains(., 'Submit')]")

        def click(self):
            # In PF5 wizard, try multiple possible submit buttons
            # 1. Try the parent's submit_button (might be on review step)
            if hasattr(self.parent, 'submit_button') and self.parent.submit_button.is_displayed:
                self.parent.submit_button.click()
            # 2. Try "Run on selected hosts" button (immediate execution)
            elif (
                hasattr(self.parent, 'run_on_selected')
                and self.parent.run_on_selected.is_displayed
                and self.parent.run_on_selected.is_enabled
            ):
                self.parent.run_on_selected.click()
            # 3. Fall back to any button with "Submit" text
            elif self.submit.is_displayed:
                self.submit.click()
            else:
                raise Exception(
                    'No submit button found. Available buttons: Next={}, Run on selected={}, Submit={}'.format(
                        self.parent.next_button.is_displayed
                        if hasattr(self.parent, 'next_button')
                        else 'N/A',
                        self.parent.run_on_selected.is_displayed
                        if hasattr(self.parent, 'run_on_selected')
                        else 'N/A',
                        self.submit.is_displayed,
                    )
                )

    def after_fill(self, was_change):
        """Override after_fill to handle PF5 wizard navigation.

        The PF5 wizard requires clicking 'Next' to progress through steps,
        unlike the old expander-based approach.
        """
        # After filling the view, we need to navigate through wizard steps
        # The fill() method will handle individual fields, but we need to
        # click Next buttons to progress through the wizard
        pass

    def fill(self, values):
        """Custom fill method for PF5 wizard that navigates through steps.

        The PF5 wizard pattern requires:
        1. Fill fields in current step
        2. Click "Next" to advance
        3. Repeat for each step
        4. Click "Submit" at the end
        """
        was_change = False

        # Helper function to safely click Next and wait
        def click_next_if_available():
            if self.next_button.is_displayed and self.next_button.is_enabled:
                self.next_button.click()
                # Wait for page to be safe after clicking Next
                self.browser.plugin.ensure_page_safe()
                # Wait a moment for the next step to load
                sleep(1)

        # Step 1: Category and template
        cat_template_values = {
            k.split('.', 1)[1]: v
            for k, v in values.items()
            if k.startswith('category_and_template.')
        }
        if cat_template_values:
            changed = self.category_and_template.fill(cat_template_values)
            was_change = was_change or changed
            click_next_if_available()

        # Step 2: Target hosts and inputs
        target_values = {
            k.split('.', 1)[1]: v
            for k, v in values.items()
            if k.startswith('target_hosts_and_inputs.')
        }
        if target_values:
            changed = self.target_hosts_and_inputs.fill(target_values)
            was_change = was_change or changed
            click_next_if_available()

        # Step 3: Advanced fields (optional - skip if no values)
        advanced_values = {
            k.split('.', 1)[1]: v for k, v in values.items() if k.startswith('advanced_fields.')
        }
        if advanced_values:
            changed = self.advanced_fields.fill(advanced_values)
            was_change = was_change or changed

        # Always click Next after advanced fields to get to Schedule step
        # (even if we didn't fill anything in advanced fields)
        click_next_if_available()

        # Step 4: Schedule - Type of execution
        schedule_values = {
            k.split('.', 1)[1]: v
            for k, v in values.items()
            if k.startswith('schedule.') and not k.startswith('schedule_')
        }
        if schedule_values:
            changed = self.schedule.fill(schedule_values)
            was_change = was_change or changed

        # Step 4a: Schedule - Future execution substep
        future_values = {
            k.split('.', 1)[1]: v
            for k, v in values.items()
            if k.startswith('schedule_future_execution.')
        }
        if future_values:
            # Need to navigate to the future execution step
            click_next_if_available()
            changed = self.schedule_future_execution.fill(future_values)
            was_change = was_change or changed

        # Step 4b: Schedule - Recurring execution substep
        recurring_values = {
            k.split('.', 1)[1]: v
            for k, v in values.items()
            if k.startswith('schedule_recurring_execution.')
        }
        if recurring_values:
            click_next_if_available()
            changed = self.schedule_recurring_execution.fill(recurring_values)
            was_change = was_change or changed

        return was_change

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        if not breadcrumb_loaded:
            return False

        # Helper to check wizard elements as fallback
        def _check_wizard_elements():
            try:
                return self.category_and_template.job_category.is_displayed
            except (AttributeError, NoSuchElementException):
                return False

        # Check breadcrumb structure
        try:
            locations = self.breadcrumb.locations
            if not locations or locations[0] != 'Jobs':
                return _check_wizard_elements()
        except (AttributeError, NoSuchElementException):
            return _check_wizard_elements()

        # PF5 UI shows "Run job", legacy shows "Job invocation"
        try:
            breadcrumb_text = self.breadcrumb.read()
            return breadcrumb_text in ['Job invocation', 'Run job']
        except (AttributeError, NoSuchElementException):
            return _check_wizard_elements()


class JobInvocationStatusView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    title = PF5OUIAText(component_id='breadcrumb_title')
    create_report = PF5OUIAButton(component_id='button-create-report')
    actions = PF5OUIADropdown(component_id='job-invocation-global-actions-dropdown')
    rerun_all = PF5OUIAButton(component_id='button-rerun-all')
    BREADCRUMB_LENGTH = 2

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.breadcrumb.wait_displayed()
        title_loaded = self.title.wait_displayed() and self.title.read() != ''

        # Check breadcrumb structure
        if not (breadcrumb_loaded and title_loaded):
            return False

        try:
            breadcrumb_ok = (
                self.breadcrumb.locations[0] == 'Jobs'
                and len(self.breadcrumb.locations) == self.BREADCRUMB_LENGTH
            )
        except (AttributeError, IndexError, NoSuchElementException):
            breadcrumb_ok = False

        if not breadcrumb_ok:
            return False

        # For scheduled jobs, the status widget might not appear immediately
        # Try to wait for it, but don't fail if it's not there
        # (it will appear when the job starts running)
        try:
            data_loaded, _ = wait_for(
                func=lambda: self.status.is_displayed,
                timeout=10,  # Reduced from 60s - don't wait too long
                delay=2,  # Reduced from 15s
                fail_func=None,  # Don't refresh - can cause issues
            )
        except TimedOutError:
            # Status widget not displayed yet (normal for scheduled jobs)
            # As long as breadcrumb and title are loaded, we're on the right page
            data_loaded = True

        return breadcrumb_loaded and title_loaded and data_loaded and breadcrumb_ok

    def wait_for_result(self, timeout=600, delay=1):
        """Wait for invocation job(s) to finish"""
        wait_for(
            lambda: self.is_displayed,
            timeout=timeout,
            delay=delay,
            logger=self.logger,
        )
        wait_for(
            lambda: self.status.read()['In Progress'] == 0,
            timeout=timeout,
            delay=1,
            logger=self.logger,
        )
        self.browser.refresh()

    @View.nested
    class overall_status(DonutCircle):
        """The donut circle with the overall job status of '{succeeded hosts}/{total hosts}'"""

        def read(self):
            """Return `dict` with the parsed overall status numbers, for example:
            ```{'succeeded_hosts': 2, 'total_hosts': 5, 'is_success': False}```

            The 'is_success' key was artificially added for convenience, to check the overall job status.
            Note: Any running or pending job will return negative result (False).
            For scheduled jobs that haven't started, returns empty dict.
            """
            if not self.is_displayed:
                return {}
            try:
                succeeded_hosts, total_hosts = [int(value) for value in self.labels[0].split('/')]
                is_success = total_hosts > 0 and total_hosts == succeeded_hosts
                return {
                    'succeeded_hosts': succeeded_hosts,
                    'total_hosts': total_hosts,
                    'is_success': is_success,
                }
            except (AttributeError, IndexError, ValueError, NoSuchElementException):
                # If reading fails (e.g., for scheduled jobs), return empty
                return {}

    @View.nested
    class status(DonutLegend):
        """'System status' panel."""

        ROOT = ".//div[contains(@class, 'chart-legend')]"
        first_label = Text(locator="//*[@id='legend-labels-0']")

        @property
        def is_displayed(self):
            """Any status label is displayed after all data are loaded."""
            try:
                return self.first_label.is_displayed
            except (AttributeError, NoSuchElementException):
                # Widget might not exist for scheduled jobs
                return False

        def read(self):
            """Return `dict` with the System status info.
            Example: ```{'Succeeded': 2, 'Failed': 1, 'In Progress': 0, 'Canceled': 0}```

            For scheduled jobs that haven't started, returns empty dict.
            """
            if not self.is_displayed:
                return {}
            try:
                return {item['label']: int(item['value']) for item in self.all_items}
            except (AttributeError, KeyError, ValueError, NoSuchElementException):
                # If reading fails (e.g., for scheduled jobs), return empty
                return {}

    @View.nested
    class overview(DescriptionList):
        ROOT = ".//dl[contains(@class, 'job-overview-description-list')]"

        def read(self):
            """Return `dict` without trailing ':' in the key names."""
            return {key.replace(':', ''): val for key, val in super().read().items()}

    @View.nested
    class target_hosts(PF5LabeledExpandableSection):
        label = 'Target Hosts'
        search_query = Text('./div[contains(@class, "-c-expandable-section__content")]/pre')
        data = PF5DataList()

        def read(self):
            return {'search_query': self.search_query.read(), 'data': self.data.read()}

    @View.nested
    class user_inputs(PF5LabeledExpandableSection):
        label = 'User Inputs'
        data = PF5DataList()

        def read(self):
            return {'data': self.data.read()}

    @View.nested
    class leapp_preupgrade_report(View):
        """LEAPP Preupgrade Report view placeholder.
        This part has not been implemented yet to the new job details page.
        Needed for bug SAT-28216
        """

        pass

    @View.nested
    class hosts(View):
        table = HostsExpandableTable(
            component_id='job-invocation-hosts-table',
            column_widgets={
                1: Checkbox(locator='.//input[@type="checkbox"]'),
                'Name': Text('./a'),
                'Host group': Text('./a'),
                'OS': Text('./a'),
                'Capsule': Text('./a'),
                'Status': Text('./span'),
            },
        )

        def read(self):
            return self.table.read()
