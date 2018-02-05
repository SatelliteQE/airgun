from airgun.entities.base import BaseEntity
from airgun.views.architecture import ArchitectureView


class ArchitectureEntity(BaseEntity):

    def create_architecture(self, values):
        view = self.navigate_to(ArchitectureView, 'New')
        view.fill(values)
        view.submit_data()

    def search(self, value):
        view = self.navigate_to(ArchitectureView, 'All')
        return view.search_element.search(value)
