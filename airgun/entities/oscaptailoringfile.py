from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.oscaptailoringfile import (
    SCAPTailoringFileCreateView,
    SCAPTailoringFileEditView,
    SCAPTailoringFilesView,
)


class OSCAPTailoringFileEntity(BaseEntity):

    def create(self, values):
        """Creates new SCAP

        :param values: Parameters to be assigned to new SCAP Tailoring File,
            mandatory values are Name and Scap file.
        """
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete corresponding SCAP Tailoring File

        :param entity_name: name of the corresponding SCAP Tailoring File
        """
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, entity_name):
        """Search for SCAP Tailoring File

        :param entity_name: name of the corresponding SCAP Tailoring File
        :return: result of the SCAP Tailoring File search
        """
        view = self.navigate_to(self, 'All')
        return view.search(entity_name)

    def read(self, entity_name):
        """Reads the content of corresponding SCAP Tailoring File

        :param entity_name: specify corresponding SCAP Tailoring File
        :return: dict representing tabs, with nested dicts representing fields
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values):
        """Updates instance of SCAP Tailoring File with new values

        :param entity_name: specify corresponding SCAP Tailoring File
        :param values: updates individual parameters of corresponding
            SCAP Tailoring File
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(OSCAPTailoringFileEntity, 'All')
class ShowAllSCAPTailoringFiles(NavigateStep):
    """Navigate to All SCAP Tailoring File screen."""
    VIEW = SCAPTailoringFilesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Tailoring Files')


@navigator.register(OSCAPTailoringFileEntity, 'New')
class UploadNewSCAPTailoringFile(NavigateStep):
    """Navigate to upload new SCAP Tailoring File page."""
    VIEW = SCAPTailoringFileCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(OSCAPTailoringFileEntity, 'Edit')
class EditSCAPTailoringFile(NavigateStep):
    """Navigate to edit existing SCAP Tailoring File page."""
    VIEW = SCAPTailoringFileEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Actions'].widget.fill('Edit')
