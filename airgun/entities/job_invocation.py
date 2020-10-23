from navmazing import NavigateToSibling
from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.job_invocation import JobInvocationCreateView
from airgun.views.job_invocation import JobInvocationStatusView
from airgun.views.job_invocation import JobInvocationsView


class JobInvocationEntity(BaseEntity):
    endpoint_path = '/job_invocations'

    def run(self, values):
        """Run specific job"""
        view = self.navigate_to(self, 'Run')
        view.fill(values)
        view.submit.click()

    def search(self, value):
        """Search for specific job invocation"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, host_name, widget_names=None):
        """Read values for scheduled or already executed job"""
        view = self.navigate_to(self, 'Job Status', entity_name=entity_name, host_name=host_name)
        return view.read(widget_names=widget_names)

    def wait_job_invocation_state(self, entity_name, host_name, expected_state='succeeded'):
        """Check job invocation state from table view"""
        view = self.navigate_to(self, 'All')
        view.search(f'host = {host_name}')
        wait_for(
            lambda: view.table.row(description=entity_name)['Status'].read() == expected_state,
            timeout=300,
            delay=10,
            fail_func=view.browser.refresh,
            logger=view.logger,
        )


@navigator.register(JobInvocationEntity, 'All')
class ShowAllJobs(NavigateStep):
    """Navigate to All Job Invocations screen."""

    VIEW = JobInvocationsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Monitor', 'Jobs')


@navigator.register(JobInvocationEntity, 'Run')
class RunNewJob(NavigateStep):
    """Navigate to Create new Job Invocation screen."""

    VIEW = JobInvocationCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(JobInvocationEntity, 'Job Status')
class JobStatus(NavigateStep):
    """Navigate to Job Invocation status screen.

    Args:
       entity_name: name of the job
       host_name: name of the host to which job was applied
    """

    VIEW = JobInvocationStatusView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.search('host = {}'.format(kwargs.get('host_name')))
        self.parent.table.row(description=kwargs.get('entity_name'))['Description'].widget.click()
