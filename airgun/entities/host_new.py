from airgun.entities.host import HostEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.host_new import NewHostDetailsView


class NewHostEntity(HostEntity):
    def get_details(self, entity_name, widget_names=None):
        """Read host values from Host Details page, optionally only the widgets in widget_names
        will be read.
        """
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        return view.read(widget_names=widget_names)


@navigator.register(NewHostEntity, 'NewDetails')
class ShowNewHostDetails(NavigateStep):
    """Navigate to Host Details page by clicking on necessary host name in the table

    Args:
        entity_name: name of the host
    """

    VIEW = NewHostDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
