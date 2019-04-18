from wait_for import wait_for
from widgetastic.widget import (
    Checkbox,
    Select,
    TableColumn,
    TableRow,
    Text,
)

from airgun.views.common import (
    BaseLoggedInView,
    BreadCrumb,
    SearchableViewMixin,
    SatTable,
)
from airgun.views.host import HostCreateView
from airgun.widgets import (
    ActionsDropdown,
    FilteredDropdown,
    SatTableWithoutHeaders,
)


class DiscoveredHostsViewTable(SatTable):
    """Discovered hosts table that has a different no rows message location.

    Example html representation::

        <div id="content">
            <table ...>

            </table>
            No entries found
        </div>
    """
    no_rows_message = (
        "//div[@id='content' and contains(., 'No entries found')]")


class DiscoveredHostsView(BaseLoggedInView, SearchableViewMixin):
    """Main discovered hosts view"""
    title = Text("//h1[contains(., 'Discovered Hosts')]")
    actions = ActionsDropdown("//div[@id='submit_multiple']")
    table = DiscoveredHostsViewTable(
        './/table',
        column_widgets={
            0: Checkbox(
                locator=".//input[contains(@id, 'host_ids')]"),
            'Name': Text("./a"),
        }
    )
    # This view has no welcome message
    welcome_message = None

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None

    def is_searchable(self):
        """Verify that search procedure can be executed against discovered
        hosts page. That means that we have search field present.

        Note: When no discovered host exists in the system the search box does
        not exist in the DOM. Also there is no welcome_message.
        """
        # This View is searchable if search field is displayed.
        return self.searchbox.search_field.is_displayed


class DiscoveredHostDetailsTableColumn(TableColumn):
    """A Table column for Discovered host details Table Row"""
    def __locator__(self):
        return self.browser.element(
            './*[self::th or self::td][{0}]'.format(self.position + 1),
            parent=self.parent
        )


class DiscoveredHostDetailsTableRow(TableRow):
    """A Table Row for Discovered host details Table"""
    Column = DiscoveredHostDetailsTableColumn


class DiscoveredHostDetailsTable(SatTableWithoutHeaders):
    """A Table represented by two columns where the property name is the first
    column and the property value is the second column.

    Example html representation::

        <table>
            <tbody>
                <tr>
                    <th><strong> architecture </strong></th>
                    <td>x86_64</td>
                </tr>
                <tr>
                    <th><strong> discovery_bootif </strong></th>
                    <td>52:d2:5f:73:31:e2</td>
                </tr>
                <tr>
                    <th><strong> discovery_bootip</strong></th>
                    <td>10.8.212.60</td>
                </tr>
    """
    Row = DiscoveredHostDetailsTableRow

    def read(self):
        """Transform rows to a dict {property_name: property_value ...}."""
        properties = super().read()
        return {
            prop['column0']: prop['column1'] for prop in properties if prop['column1']}


class DiscoveredHostDetailsView(BaseLoggedInView):
    """Discovered Host details view"""
    breadcrumb = BreadCrumb()
    back = Text(
        ".//a[contains(@class, 'btn') and @data-id='aid_discovered_hosts']")
    actions = ActionsDropdown(
        "//div[contains(@class, 'btn-group')][a[@data-toggle='dropdown']]")
    delete = Text(".//a[contains(@data-confirm, 'Delete')]")
    expand_all = Text(".//a[@id='expand_all']")
    interfaces = SatTable("//div[@id='interfaces-panel']/table")
    highlights = DiscoveredHostDetailsTable(
        "//div[@id='category-highlights']//table")
    storage = DiscoveredHostDetailsTable(
        "//div[@id='category-storage']//table")
    hardware = DiscoveredHostDetailsTable(
        "//div[@id='category-hardware']//table")
    network = DiscoveredHostDetailsTable(
        "//div[@id='category-network']//table")
    software = DiscoveredHostDetailsTable(
        "//div[@id='category-software']//table")
    miscellaneous = DiscoveredHostDetailsTable(
        "//div[@id='category-miscellaneous']//table")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Discovered hosts'
                and self.breadcrumb.locations[1].startswith('Discovered host:')
        )


class DiscoveredHostsActionDialog(BaseLoggedInView):
    """Common dialog view for all discovered hosts actions"""
    title = None
    table = SatTable("//div[@class='modal-body']//table")
    submit = Text("//button[@onclick='submit_modal_form()']")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class DiscoveredHostsAutoProvisionDialog(DiscoveredHostsActionDialog):
    """Discovered hosts Auto Provision action dialog view"""
    title = Text(
        "//h4[text()='Auto Provision"
        " - The following hosts are about to be changed']"
    )


class DiscoveredHostsAssignOrganizationDialog(DiscoveredHostsActionDialog):
    """Discovered hosts Assign Organization action dialog view"""
    title = Text(
        "//h4[text()='Assign Organization"
        " - The following hosts are about to be changed']"
    )
    organization = Select(id='organization_id')


class DiscoveredHostsAssignLocationDialog(DiscoveredHostsActionDialog):
    """Discovered hosts Assign Location action dialog view"""
    title = Text(
        "//h4[text()='Assign Location"
        " - The following hosts are about to be changed']"
    )
    location = Select(id='location_id')


class DiscoveredHostsRebootDialog(DiscoveredHostsActionDialog):
    """Discovered hosts Reboot dialog action view"""
    title = Text(
        "//h4[text()='Reboot"
        " - The following hosts are about to be changed']"
    )


class DiscoveredHostsDeleteDialog(DiscoveredHostsActionDialog):
    """Discovered hosts Delete dialog action view"""
    title = Text(
        "//h4[text()='Delete"
        " - The following hosts are about to be changed']"
    )


class DiscoveredHostProvisionDialog(BaseLoggedInView):
    """Discovered host Provision action dialog view"""
    ROOT = ".//div[@class='modal-content']"
    title = Text(".//h4[text()='Select initial host properties']")
    host_group = FilteredDropdown(id='host_hostgroup_id')
    organization = FilteredDropdown(id='host_organization_id')
    location = FilteredDropdown(id='host_location_id')
    cancel = Text(".//button[@data-dismiss='modal']")
    customize_create = Text(
        ".//input[@type='submit'][not(@name='quick_submit')]")
    quick_create = Text(".//input[@type='submit'][@name='quick_submit']")

    @property
    def is_displayed(self):
        return (self.browser.wait_for_element(
            self.title, exception=False) is not None
                and self.browser.is_displayed(self.title))

    @property
    def is_all_displayed(self):
        """Check that all the required dialog widgets fields are displayed"""
        return all([
            self.is_displayed,
            self.host_group.is_displayed,
            self.organization.is_displayed,
            self.location.is_displayed
        ])

    def before_fill(self, values=None):
        """Before filling we have to wait and ensure that all the required
        dialog widgets fields are visible.
        """
        wait_for(
            lambda: self.is_all_displayed,
            timeout=10,
            delay=1,
            logger=self.logger
        )


class DiscoveredHostEditProvisioningView(HostCreateView):
    """Discovered Host Edit Provisioning View,

    Note: When we click on customize_create in dialog
        DiscoveredHostProvisionDialog, the user is redirect to this view.
    """

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Discovered hosts'
                and self.breadcrumb.locations[1].startswith('Provision')
        )
