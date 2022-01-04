from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.utils import retry_navigation
from airgun.views.media import MediaCreateView
from airgun.views.media import MediaEditView
from airgun.views.media import MediumView


class MediaEntity(BaseEntity):
    endpoint_path = '/media'

    def create(self, values):
        """Create new media"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for specific media"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read values for existing media"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values):
        """Update media values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete media"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.click(handle_alert=True)


@navigator.register(MediaEntity, 'All')
class ShowAllMedium(NavigateStep):
    """Navigate to All Medium screen."""

    VIEW = MediumView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Installation Media')


@navigator.register(MediaEntity, 'New')
class AddNewMedia(NavigateStep):
    """Navigate to Create new Media screen."""

    VIEW = MediaCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(MediaEntity, 'Edit')
class EditMedia(NavigateStep):
    """Navigate to Edit Media screen.

    Args:
       entity_name: name of media
    """

    VIEW = MediaEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
