from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.oscapreport import (
    RemediateModal,
    SCAPReportDetailsView,
    SCAPReportView,
)


class OSCAPReportEntity(BaseEntity):
    endpoint_path = '/compliance/arf_reports'

    def search(self, search_string):
        """Search for SCAP Report

        :param search_string: how to find the SCAP Report
        :return: result of the SCAP Report search
        """
        view = self.navigate_to(self, 'All')
        return view.search(search_string)

    def details(self, search_string, widget_names=None, limit=None):
        """Read the content from corresponding SCAP Report dashboard,
            clicking on the link in Reported At column of
            SCAP Report list

        :param search_string:
        :param limit: how many rules results to fetch at most
        :return: list of dictionaries with values from SCAP Report Details View
        """
        view = self.navigate_to(self, 'Details', search_string=search_string)
        return view.read(widget_names=widget_names, limit=limit)

    def remediate(self, search_string, resource):
        """Remediate the failed rule using automatic remediation through Ansible

        :param search_string:
        """
        view = self.navigate_to(self, 'Details', search_string=search_string)
        view.table.row(resource=resource).actions.fill('Remediation')
        view = RemediateModal(self.browser)

        wait_for(lambda: view.title.is_displayed, timeout=10, delay=1)
        view.fill({'select_remediation_method.snippet': 'Ansible'})
        view.select_capsule.run.click()


@navigator.register(OSCAPReportEntity, 'All')
class ShowAllSCAPReports(NavigateStep):
    """Navigate to Compliance Reports screen."""

    VIEW = SCAPReportView

    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Compliance', 'Reports')


@navigator.register(OSCAPReportEntity, 'Details')
class DetailsSCAPReport(NavigateStep):
    """To get data from ARF report view

    Args:
    search_string: what to fill to find the SCAP report
    """

    VIEW = SCAPReportDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        search_string = kwargs.get('search_string')
        self.parent.search(search_string)
        self.parent.table.row()['Reported At'].widget.click()
