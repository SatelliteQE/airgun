from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.file import FileDetailsView, FilesView


class FilesEntity(BaseEntity):
    endpoint_path = "/files"

    def search(self, query):
        view = self.navigate_to(self, "All")
        return view.search(query)

    def read(self, entity_name, widget_names=None):
        view = self.navigate_to(self, "Details", entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def read_cv_table(self, entity_name):
        view = self.navigate_to(self, "Details", entity_name=entity_name)
        return view.content_views.cvtable.read()


@navigator.register(FilesEntity, "All")
class ShowAllFiles(NavigateStep):
    """navigate to Files Page"""

    VIEW = FilesView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select("Content", "Content Types", "Files")


@navigator.register(FilesEntity, "Details")
class ShowPackageDetails(NavigateStep):
    """Navigate to File Details page by clicking on file name"""

    VIEW = FileDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, "All")

    def step(self, *args, **kwargs):
        entity_name = kwargs.get("entity_name")
        self.parent.search(f"name = {entity_name}")
        self.parent.table.row(name=entity_name)["Name"].widget.click()

    def am_i_here(self, *args, **kwargs):
        entity_name = kwargs.get("entity_name")
        self.view.file_name = entity_name
        return (
            self.view.is_displayed and self.view.breadcrumb.locations[1] == entity_name
        )
