from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStepWithWait as NavigateStep, navigator
from airgun.views.cloud_compliance import (
    ComplianceReportDetailsView,
    ComplianceReportsView,
    CreatePolicyWizardView,
    ScapPoliciesView,
    ScapPolicyDetailsView,
)
from airgun.views.common import BaseLoggedInView


class CloudComplianceReportsEntity(BaseEntity):
    """Airgun entity for the Insights Compliance Reports page."""

    endpoint_path = '/foreman_rh_cloud/insights_compliance/reports'

    def read(self):
        """Navigate to the Compliance Reports page and return all table rows."""
        view = self.navigate_to(self, 'All')
        wait_for(lambda: view.reports_table.is_displayed, timeout=30, handle_exception=True)
        return view.reports_table.read()

    def get_report_details(self, policy_name):
        """Click a policy link in the reports table and return the detail view."""
        view = self.navigate_to(self, 'Details', policy_name=policy_name)
        wait_for(lambda: view.is_displayed, timeout=30, handle_exception=True)
        return view

    def search(self, value, column='Policy name'):
        """Filter the reports table by selecting a column and typing a search value."""
        view = self.navigate_to(self, 'All')
        wait_for(lambda: view.reports_table.is_displayed, timeout=30, handle_exception=True)
        view.filter_toggle.fill(column)
        view.filter_input.fill(value)
        return view.reports_table.read()


@navigator.register(CloudComplianceReportsEntity, 'All')
class ShowComplianceReportsView(NavigateStep):
    """Navigate to the Insights Compliance Reports listing page."""

    VIEW = ComplianceReportsView
    WAIT_TIMEOUT = 40

    def step(self, *args, **kwargs):
        main_view = self.create_view(BaseLoggedInView)
        main_view.menu.select('Insights', 'Compliance Reports')


@navigator.register(CloudComplianceReportsEntity, 'Details')
class ShowComplianceReportDetailsView(NavigateStep):
    """Navigate to a specific Compliance Report detail page."""

    VIEW = ComplianceReportDetailsView
    WAIT_TIMEOUT = 40

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        policy_name = kwargs.get('policy_name')
        self.parent.reports_table.row(Policy__contains=policy_name)['Policy'].widget.click()


class CloudCompliancePoliciesEntity(BaseEntity):
    """Airgun entity for the Insights Compliance SCAP Policies page."""

    endpoint_path = '/foreman_rh_cloud/insights_compliance/scappolicies'

    def read(self):
        """Navigate to the SCAP Policies page and return all table rows."""
        view = self.navigate_to(self, 'All')
        wait_for(lambda: view.policies_table.is_displayed, timeout=30, handle_exception=True)
        return view.policies_table.read()

    def get_policy_details(self, policy_name):
        """Click a policy link in the table and return the detail view."""
        view = self.navigate_to(self, 'Details', policy_name=policy_name)
        wait_for(lambda: view.is_displayed, timeout=30, handle_exception=True)
        return view

    def create_policy(self):
        """Open the Create Policy wizard and return the wizard view."""
        view = self.navigate_to(self, 'New')
        wait_for(lambda: view.is_displayed, timeout=30, handle_exception=True)
        return view


@navigator.register(CloudCompliancePoliciesEntity, 'Details')
class ShowScapPolicyDetailsView(NavigateStep):
    """Navigate to a specific SCAP Policy detail page."""

    VIEW = ScapPolicyDetailsView
    WAIT_TIMEOUT = 40

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        policy_name = kwargs.get('policy_name')
        self.parent.policies_table.open_policy_details(policy_name)


@navigator.register(CloudCompliancePoliciesEntity, 'All')
class ShowScapPoliciesView(NavigateStep):
    """Navigate to the Insights Compliance SCAP Policies listing page."""

    VIEW = ScapPoliciesView
    WAIT_TIMEOUT = 40

    def step(self, *args, **kwargs):
        main_view = self.create_view(BaseLoggedInView)
        main_view.menu.select('Insights', 'SCAP Policies')


@navigator.register(CloudCompliancePoliciesEntity, 'New')
class CreateScapPolicyWizard(NavigateStep):
    """Open the Create Policy wizard from the SCAP Policies page."""

    VIEW = CreatePolicyWizardView
    WAIT_TIMEOUT = 40

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.create_policy.click()
