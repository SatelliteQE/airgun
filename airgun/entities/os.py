from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.os import (
    OperatingSystemCreateView,
    OperatingSystemEditView,
    OperatingSystemsView,
)


class OperatingSystemEntity(BaseEntity):
    endpoint_path = "/operatingsystems"

    def create(self, values):
        """Create new operating system entity"""
        view = self.navigate_to(self, "New")
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name, cancel=False):
        """Remove existing operating system entity"""
        view = self.navigate_to(self, "All")
        view.search(entity_name)
        view.table.row(title__endswith=entity_name)["Actions"].widget.fill("Delete")
        self.browser.handle_alert(cancel=cancel)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for operating system entity"""
        view = self.navigate_to(self, "All")
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read all values for created operating system entity"""
        view = self.navigate_to(self, "Edit", entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values):
        """Update necessary values for operating system"""
        view = self.navigate_to(self, "Edit", entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(OperatingSystemEntity, "All")
class ShowAllOperatingSystems(NavigateStep):
    """Navigate to All Operating Systems page"""

    VIEW = OperatingSystemsView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select("Hosts", "Provisioning Setup", "Operating Systems")


@navigator.register(OperatingSystemEntity, "New")
class AddNewOperatingSystem(NavigateStep):
    """Navigate to Create Operating System page"""

    VIEW = OperatingSystemCreateView

    prerequisite = NavigateToSibling("All")

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(OperatingSystemEntity, "Edit")
class EditOperatingSystem(NavigateStep):
    """Navigate to Edit Operating System page

    Args:
        entity_name: name of the operating system
    """

    VIEW = OperatingSystemEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, "All")

    def step(self, *args, **kwargs):
        entity_name = kwargs.get("entity_name")
        self.parent.search(entity_name)
        self.parent.table.row(title__endswith=entity_name)["Title"].widget.click()
