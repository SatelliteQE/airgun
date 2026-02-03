from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.bootc import BootedContainerImagesView


class BootcEntity(BaseEntity):
    endpoint_path = '/booted_container_images'

    def read(self, booted_image_name):
        """
        Read the expanded row of a specific booted_image, returns a tuple
        with the unexpanded content, and the expanded content
        """
        view = self.navigate_to(self, 'All')
        view.search(f'bootc_booted_image = {booted_image_name}')
        view.table.row(image_name=booted_image_name).expand()
        row = view.table.row(image_name=booted_image_name).read()
        row_content = view.table.row(image_name=booted_image_name).content.read()
        return (row, row_content['table'][0])


@navigator.register(BootcEntity, 'All')
class BootedImagesScreen(NavigateStep):
    """Navigate to Booted Container Images screen."""

    VIEW = BootedContainerImagesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Booted Container Images')
