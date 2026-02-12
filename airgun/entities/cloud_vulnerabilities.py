from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.cloud_vulnerabilities import (
    CloudVulnerabilityView,
    CVEDetailsView,
    EditVulnerabilitiesModal,
)
from airgun.views.host_new import NewHostDetailsView


class CloudVulnerabilityEntity(BaseEntity):
    endpoint_path = '/foreman_rh_cloud/insights_vulnerability'

    def read(self, entity_name=None, widget_names=None):
        """
        Read vulnerabilities table data including Business risk and Status columns

        Returns:
            list: List of dictionaries with CVE data including new columns
        """
        view = self.navigate_to(self, 'All')
        wait_for(lambda: view.vulnerabilities_table.is_displayed, timeout=30)
        return view.vulnerabilities_table.read()

    def _navigate_to_cve_details(self, cve_id):
        """Helper method to navigate to CVE details page"""
        view = self.navigate_to(self, 'All')
        view.wait_displayed(timeout='30s')
        wait_for(lambda: view.vulnerabilities_table.is_displayed, timeout=30)
        view.search_bar.fill(cve_id)
        view.browser.element(f'.//a[contains(@href, "{cve_id}")]').click()

    def get_cve_details(self, cve_id):
        """
        Read CVE details from CVE details page

        Args:
            cve_id (str): CVE ID to get details
        """
        self._navigate_to_cve_details(cve_id)
        view = CVEDetailsView(self.browser)
        return view.read()

    def get_affected_hosts_by_cve(self, cve_id):
        """
        Get list of affected hosts for a specific CVE

        Args:
            cve_id (str): CVE ID to get affected hosts for
        """
        self._navigate_to_cve_details(cve_id)
        cve_details_view = CVEDetailsView(self.browser)
        wait_for(lambda: cve_details_view.affected_hosts_table.is_displayed, timeout=30)
        return cve_details_view.affected_hosts_table.read()

    def validate_cve_to_host_details_flow(self, cve_id, hostname=None):
        """
        Complete flow: CVE details -> affected hosts -> click host -> host details page

        Args:
            cve_id (str): CVE ID to test
            hostname (str, optional): Specific host name to click on.
        """
        self._navigate_to_cve_details(cve_id)
        cve_details_view = CVEDetailsView(self.browser)
        wait_for(lambda: cve_details_view.affected_hosts_table.is_displayed, timeout=30)
        cve_details_view.search_bar.fill(hostname)
        cve_details_view.browser.element(f'.//a[contains(text(), "{hostname}")]').click()
        host_details_view = NewHostDetailsView(self.browser)
        host_details_view.breadcrumb.wait_displayed()
        wait_for(
            lambda: host_details_view.vulnerabilities.vulnerabilities_table.is_displayed, timeout=30
        )
        vulnerabilities = getattr(host_details_view.vulnerabilities, 'vulnerabilities_table', None)
        if vulnerabilities is not None:
            return vulnerabilities.read()
        else:
            return []

    def edit_vulnerabilities(self, cve_id, status='In review'):
        """Helper method to navigate to CVE details page"""
        self._navigate_to_cve_details(cve_id)
        view = CVEDetailsView(self.browser)
        wait_for(lambda: view.affected_hosts_table.is_displayed, timeout=30)
        view.actions.item_select('Edit status')
        modal = EditVulnerabilitiesModal(self.browser)
        wait_for(lambda: modal.is_displayed, handle_exception=True, timeout=10)
        modal.status.fill(status)
        modal.justification_note.fill('test')
        modal.save.click()

    def read_no_authorized_message(self):
        view = self.navigate_to(self, 'All')
        wait_for(lambda: view.title.is_displayed, timeout=30)
        wait_for(lambda: view.no_authorized_header.is_displayed, timeout=30)
        return view.no_authorized_header.read()

    def edit_business_risk(self, cve_id, risk_level, justification=None):
        """
        Edit business risk for a single CVE from the main vulnerabilities page

        Args:
            cve_id (str): CVE ID to edit (e.g., "CVE-2025-8058")
            risk_level (str): One of: "Critical", "High", "Medium", "Low", "Not defined"
            justification (str, optional): Justification note text

        Example:
            entity.edit_business_risk("CVE-2025-8058", "High", "Critical system component")
        """
        view = self.navigate_to(self, 'All')
        wait_for(lambda: view.vulnerabilities_table.is_displayed, timeout=30)

        # Search for the CVE
        view.search_bar.fill(cve_id)

        # Find the row and open row kebab menu
        row = view.vulnerabilities_table.row(**{'CVE ID': cve_id})
        row['Column with row actions'].widget.item_select('Edit business risk')

        # Fill the modal
        modal = view.edit_business_risk_modal
        wait_for(lambda: modal.is_displayed, timeout=10)

        # Select the risk level radio button
        risk_map = {
            'Critical': modal.critical,
            'High': modal.high,
            'Medium': modal.medium,
            'Low': modal.low,
            'Not defined': modal.not_defined,
        }
        risk_map[risk_level].fill(True)

        if justification:
            modal.justification_note.fill(justification)

        modal.save.click()
        wait_for(lambda: not modal.is_displayed, timeout=10)

    def filter_by_os(self, os_versions):
        """
        Filter vulnerabilities by OS version(s) using the "Applies to OS" filter
        Supports both parent versions (e.g., "RHEL 9") and child versions (e.g., "RHEL 9.7")
        Automatically expands parent nodes when selecting child versions

        Args:
            os_versions (list): List of OS versions to filter by

        Examples:
            entity.filter_by_os(["RHEL 9"])  # Filters all RHEL 9 versions
            entity.filter_by_os(["RHEL 9.7"])  # Expands RHEL 9, selects only 9.7
            entity.filter_by_os(["RHEL 8", "RHEL 9.7"])  # Multiple versions
        """
        view = self.navigate_to(self, 'All')
        wait_for(lambda: view.vulnerabilities_table.is_displayed, timeout=30)

        # Step 1: Select "Applies to OS" from the filter type menu
        view.filter_type_menu.item_select('Applies to OS')

        # Step 2: Click the OS filter button to open the tree dropdown
        view.os_filter_button.click()
        wait_for(lambda: view.os_filter_tree.is_displayed, timeout=10)

        # Step 3: For each OS version, expand parent if needed, then select
        for os_version in os_versions:
            # Check if this is a child version (contains a dot, like "RHEL 9.7")
            if '.' in os_version:
                # Extract parent name (e.g., "RHEL 9" from "RHEL 9.7")
                parts = os_version.split()  # ["RHEL", "9.7"]
                if len(parts) >= 2:  # noqa: PLR2004
                    version_parts = parts[1].split('.')  # ["9", "7"]
                    parent_version = f'{parts[0]} {version_parts[0]}'  # "RHEL 9"

                    # Check if parent is collapsed (aria-expanded="false")
                    parent_node_locator = f'.//li[@id="{parent_version}"][@aria-expanded="false"]'
                    if view.browser.element(parent_node_locator, exception=False):
                        # Parent is collapsed, need to expand it
                        expand_button_locator = (
                            f'.//li[@id="{parent_version}"]'
                            f'//button[contains(@class, "pf-v5-c-tree-view__node-toggle")]'
                        )
                        view.browser.click(expand_button_locator)
                        # Wait a moment for the tree to expand
                        view.browser.plugin.ensure_page_safe()

            # Now check the checkbox for this OS version
            # Use direct browser click since cached_property might not include newly visible items
            checkbox_locator = f'.//li[@id="{os_version}"]//input[@type="checkbox"]'
            checkbox = view.browser.element(checkbox_locator, exception=False)
            if checkbox and not checkbox.is_selected():
                view.browser.click(checkbox_locator)

        # Close the dropdown by clicking the button again (or clicking outside)
        view.os_filter_button.click()

    def edit_business_risk_from_details(self, cve_id, risk_level, justification=None):
        """
        Edit business risk from the CVE details page using the Actions dropdown

        Args:
            cve_id (str): CVE ID to navigate to and edit
            risk_level (str): One of: "Critical", "High", "Medium", "Low", "Not defined"
            justification (str, optional): Justification note text

        Example:
            entity.edit_business_risk_from_details("CVE-2025-8058", "Low")
        """
        # Navigate to CVE details page
        self._navigate_to_cve_details(cve_id)
        view = CVEDetailsView(self.browser)
        view.wait_displayed()

        # Open Actions dropdown and select Edit business risk
        view.actions_dropdown.item_select('Edit business risk')

        # Fill the modal (same modal as main page)
        modal = view.edit_business_risk_modal
        wait_for(lambda: modal.is_displayed, timeout=10)

        # Select the risk level
        risk_map = {
            'Critical': modal.critical,
            'High': modal.high,
            'Medium': modal.medium,
            'Low': modal.low,
            'Not defined': modal.not_defined,
        }
        risk_map[risk_level].fill(True)

        if justification:
            modal.justification_note.fill(justification)

        modal.save.click()
        wait_for(lambda: not modal.is_displayed, timeout=10)

    def edit_status(self, cve_id, status, justification=None, no_overwrite=False):
        """
        Edit status for a single CVE from the main vulnerabilities page

        Args:
            cve_id (str): CVE ID to edit
            status (str): One of: "Not reviewed", "In review", "On-hold",
                         "Scheduled for patch", "Resolved", "No action - risk accepted",
                         "Resolved via mitigation"
            justification (str, optional): Justification note text
            no_overwrite (bool): Whether to check "Do not overwrite individual system status"

        Example:
            entity.edit_status("CVE-2025-8058", "In review", "Investigating impact")
        """
        view = self.navigate_to(self, 'All')
        wait_for(lambda: view.vulnerabilities_table.is_displayed, timeout=30)

        # Search for the CVE
        view.search_bar.fill(cve_id)

        # Find the row and open row kebab menu
        row = view.vulnerabilities_table.row(**{'CVE ID': cve_id})
        row['Column with row actions'].widget.item_select('Edit status')

        # Fill the modal
        modal = view.edit_status_modal
        wait_for(lambda: modal.is_displayed, timeout=10)
        modal.status_select.fill(status)

        if justification:
            modal.justification_note.fill(justification)

        # Always fill checkbox to ensure correct state (not toggle)
        modal.no_overwrite.fill(no_overwrite)

        modal.save.click()
        wait_for(lambda: not modal.is_displayed, timeout=10)

    def _select_cve_checkboxes(self, view, cve_ids):
        """Helper method to select checkboxes for multiple CVEs

        Args:
            view: The CloudVulnerabilityView instance
            cve_ids (list): List of CVE IDs to select
        """
        for cve_id in cve_ids:
            view.search_bar.fill(cve_id)
            # Find the row
            row = view.vulnerabilities_table.row(**{'CVE ID': cve_id})
            # Click the label (which will check the checkbox)
            # Get the <tr> element and find the checkbox label within it
            row_element = row.__element__()
            label_locator = './/td[contains(@class, "pf-v5-c-table__check")]//label'
            label = view.browser.element(label_locator, parent=row_element)
            label.click()
            view.search_bar.fill('')  # Clear search to show all CVEs again

    def bulk_edit_business_risk(self, cve_ids, risk_level, justification=None):
        """
        Edit business risk for multiple CVEs using bulk actions

        Args:
            cve_ids (list): List of CVE IDs to edit (e.g., ["CVE-2025-8058", "CVE-2025-1234"])
            risk_level (str): One of: "Critical", "High", "Medium", "Low", "Not defined"
            justification (str, optional): Justification note text

        Example:
            entity.bulk_edit_business_risk(["CVE-2025-8058", "CVE-2025-1234"], "High")
        """
        view = self.navigate_to(self, 'All')
        wait_for(lambda: view.vulnerabilities_table.is_displayed, timeout=30)

        # Select checkboxes for each CVE
        self._select_cve_checkboxes(view, cve_ids)

        # Use bulk actions menu instead of row kebab
        view.bulk_actions.item_select('Edit business risk')

        # Fill the modal (same as individual edit)
        modal = view.edit_business_risk_modal
        wait_for(lambda: modal.is_displayed, timeout=10)

        risk_map = {
            'Critical': modal.critical,
            'High': modal.high,
            'Medium': modal.medium,
            'Low': modal.low,
            'Not defined': modal.not_defined,
        }
        risk_map[risk_level].fill(True)

        if justification:
            modal.justification_note.fill(justification)

        modal.save.click()
        wait_for(lambda: not modal.is_displayed, timeout=10)

        # Close the bulk actions dropdown by clicking elsewhere (e.g., title)
        view.title.click()
        # Wait for the dropdown menu to actually close (elements() returns empty list when not found)
        wait_for(
            lambda: len(view.browser.elements('//div[contains(@class, "pf-v5-c-menu")]')) == 0,
            timeout=10,
        )

        # Clear the search bar to show all CVEs again
        view.search_bar.fill('')

    def bulk_edit_status(self, cve_ids, status, justification=None, no_overwrite=False):
        """
        Edit status for multiple CVEs using bulk actions

        Args:
            cve_ids (list): List of CVE IDs to edit
            status (str): Status value to set
            justification (str, optional): Justification note text
            no_overwrite (bool): Whether to check "Do not overwrite individual system status"

        Example:
            entity.bulk_edit_status(["CVE-2025-8058", "CVE-2025-1234"], "Resolved")
        """
        view = self.navigate_to(self, 'All')
        wait_for(lambda: view.vulnerabilities_table.is_displayed, timeout=30)

        # Select checkboxes for each CVE
        self._select_cve_checkboxes(view, cve_ids)

        # Use bulk actions menu
        view.bulk_actions.item_select('Edit status')

        # Fill the modal
        modal = view.edit_status_modal
        wait_for(lambda: modal.is_displayed, timeout=10)

        modal.status_select.fill(status)

        if justification:
            modal.justification_note.fill(justification)

        modal.no_overwrite.fill(no_overwrite)

        modal.save.click()
        wait_for(lambda: not modal.is_displayed, timeout=10)

        # Close the bulk actions dropdown by clicking elsewhere (e.g., title)
        view.title.click()
        # Wait for the dropdown menu to actually close (elements() returns empty list when not found)
        wait_for(
            lambda: len(view.browser.elements('//div[contains(@class, "pf-v5-c-menu")]')) == 0,
            timeout=10,
        )

        # Clear the search bar to show all CVEs again
        view.search_bar.fill('')

    def edit_status_from_details(self, cve_id, status, justification=None, no_overwrite=False):
        """
        Edit status from the CVE details page using the Actions dropdown

        Args:
            cve_id (str): CVE ID to navigate to and edit
            status (str): Status value to set
            justification (str, optional): Justification note text
            no_overwrite (bool): Whether to check "Do not overwrite individual system status"

        Example:
            entity.edit_status_from_details("CVE-2025-8058", "Resolved via mitigation")
        """
        # Navigate to CVE details page
        self._navigate_to_cve_details(cve_id)
        view = CVEDetailsView(self.browser)
        view.wait_displayed()

        # Open Actions dropdown and select Edit status
        view.actions_dropdown.item_select('Edit status')

        # Fill the modal
        modal = view.edit_status_modal
        wait_for(lambda: modal.is_displayed, timeout=10)

        modal.status_select.fill(status)

        if justification:
            modal.justification_note.fill(justification)

        modal.no_overwrite.fill(no_overwrite)

        modal.save.click()
        wait_for(lambda: not modal.is_displayed, timeout=10)


@navigator.register(CloudVulnerabilityEntity, 'All')
class ShowVulnerabilityListView(NavigateStep):
    """Navigate to main Red Hat Lightspeed -> Vulnerability page"""

    VIEW = CloudVulnerabilityView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Red Hat Lightspeed', 'Vulnerability')
