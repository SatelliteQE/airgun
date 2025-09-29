from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.entities.rhai.base import InsightsNavigateStep
from airgun.navigation import NavigateStep, navigator
from airgun.views.rhai import InventoryAllHosts, InventoryHostDetails


class InventoryHostEntity(BaseEntity):
    endpoint_path = '/redhat_access/insights/inventory'

    @property
    def total_systems(self):
        """Get number of all systems."""
        view = self.navigate_to(self, 'All')
        return view.systems_count.text.split()[0]

    def search(self, host_name):
        """Search a certain host."""
        view = self.navigate_to(self, 'All')
        view.search.fill(host_name)
        return view.table

    def read(self, entity_name, widget_names=None):
        """Read host details, optionally read only the widgets in widget_names."""
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        wait_for(lambda: view.is_displayed)
        values = view.read(widget_names=widget_names)
        # close the view dialog, as will break next entities navigation
        view.close.click()
        return values


@navigator.register(InventoryHostEntity, 'All')
class AllHosts(InsightsNavigateStep):
    """Navigate to Insights Inventory screen."""

    VIEW = InventoryAllHosts

    def step(self, *args, **kwargs):
        self.view.menu.select('Insights', 'Inventory')


@navigator.register(InventoryHostEntity, 'Details')
class HostDetails(NavigateStep):
    """Navigate to Insights Inventory screen.

    Args:
        entity_name: hostname
    """

    VIEW = InventoryHostDetails

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search.fill(entity_name)
        self.parent.table.row_by_cell_or_widget_value('System Name', entity_name)[
            'System Name'
        ].widget.click()
