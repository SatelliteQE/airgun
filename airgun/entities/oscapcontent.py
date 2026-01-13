from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.oscapcontent import (
    SCAPContentCreateView,
    SCAPContentEditView,
    SCAPContentsView,
)


class OSCAPContentEntity(BaseEntity):
    endpoint_path = '/compliance/scap_contents'

    def create(self, values):
        """Create new SCAP Conent

        :param values: Parameters to be assigned to new SCAP content,
            manadatory values are Title and Scap file.
        """
        view = self.navigate_to(self, 'New')
        view.fill(values)
        self.browser.click(view.submit, ignore_ajax=True)

        view.validations.assert_no_errors()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete corresponding SCAP Content

        :param entity_name: title of the corresponding SCAP Content
        """
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(title=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, title):
        """Search for SCAP Content

        :param title: title of the corresponding SCAP Content
        :return: result of the SCAP Content search
        """
        view = self.navigate_to(self, 'All')
        return view.search(title)

    def read(self, entity_name, widget_names=None):
        """Reads the content of corresponding SCAP Content

        :param entity_name: specify corresponding SCAP Content
        :return: dict representing tabs, with nested dicts representing fields
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values):
        """Updates instance of SCAP Content with new values

        :param entity_name: specify corresponding SCAP Content
        :param values: updates individual parameters of SCAP Content instance
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(OSCAPContentEntity, 'All')
class ShowAllSCAPContents(NavigateStep):
    """Navigate to All SCAP Contents screen."""

    VIEW = SCAPContentsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Compliance', 'SCAP contents')


@navigator.register(OSCAPContentEntity, 'New')
class UploadNewSCAPContent(NavigateStep):
    """Navigate to upload new SCAP Content page."""

    VIEW = SCAPContentCreateView

    def am_i_here(self, *args, **kwargs):
        return self.view.is_displayed and self.view.title == ''

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)


@navigator.register(OSCAPContentEntity, 'Edit')
class EditSCAPContent(NavigateStep):
    """Navigate to edit existing SCAP Content page."""

    VIEW = SCAPContentEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(title=entity_name)['Title'].widget.click()
