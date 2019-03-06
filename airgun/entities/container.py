from navmazing import NavigateToSibling
from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.container import ContainerCreateView, ContainerDetailsView, ContainersView


class ContainerEntity(BaseEntity):

    def create(self, values):
        """Create new container"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.environment.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search specific value"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read container details."""
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def set_power(self, entity_name, power):
        """Power on or power off specific container.

        Args:
            entity_name: name of container
            power: power state to set container into. May be one of "On"/"Off"/True/False.
        """
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        if power in (True, 'On'):
            view.power_on.click()
        elif power in (False, 'Off'):
            view.power_off.click(handle_alert=True)
        else:
            raise ValueError(
                'Wrong `power` value passed. Supported values are True/False/"On"/"Off"')
        # workaround for BZ1683348
        view.flash.assert_no_error(
            ignore_messages=['Error - wrong number of arguments (given 1, expected 0)'])
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete container."""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name.capitalize())['Action'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(ContainerEntity, 'All')
class ShowAllContainers(NavigateStep):
    """Navigate to All Containers screen"""
    VIEW = ContainersView

    def step(self, *args, **kwargs):
        self.view.menu.select('Containers', 'All Containers')


@navigator.register(ContainerEntity, 'New')
class AddNewContainer(NavigateStep):
    """Navigate to Create container screen"""
    VIEW = ContainerCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(ContainerEntity, 'Details')
class ContainerDetails(NavigateStep):
    """Navigate to container details screen"""
    VIEW = ContainerDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def am_i_here(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        return (
            self.view.is_displayed
            and self.view.breadcrumb.read() == '{} - /{}'.format(
                entity_name.capitalize(), entity_name)
        )

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name.capitalize())['Name'].widget.click()
