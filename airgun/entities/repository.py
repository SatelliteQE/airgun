from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.entities.product import ProductEntity
from airgun.views.repository import (
    RepositoryCreateView,
    RepositoryEditView,
    RepositoriesView,
)


class RepositoryEntity(BaseEntity):

    def create(self, product_name, values):
        """Create new repository for product"""
        view = self.navigate_to(self, 'New', product_name=product_name)
        view.fill(values)
        view.submit.click()

    def search(self, product_name, value):
        """Search for specific product repository"""
        view = self.navigate_to(self, 'All', product_name=product_name)
        return view.search(value)

    def read(self, product_name, entity_name):
        """Read values for repository"""
        view = self.navigate_to(
            self, 'Edit', product_name=product_name, entity_name=entity_name)
        return view.read()

    def update(self, product_name, entity_name, values):
        """Update product repository values"""
        view = self.navigate_to(
            self, 'Edit', product_name=product_name, entity_name=entity_name)
        view.fill(values)

    def delete(self, product_name, entity_name):
        """Delete specific product repository"""
        view = self.navigate_to(self, 'All', product_name=product_name)
        view.search(entity_name)
        view.table.row(name=entity_name)[0].fill(True)
        view.delete.click()
        view.dialog.confirm()


@navigator.register(RepositoryEntity, 'All')
class ShowAllRepositories(NavigateStep):
    """Navigate to All Product Repositories page by pressing 'Repositories'
    Tab on Product Edit View page

    Args:
        product_name: name of product
    """
    VIEW = RepositoriesView

    def am_i_here(self, *args, **kwargs):
        product_name = kwargs.get('product_name')
        return (
            self.view.is_displayed
            and self.view.breadcrumb.locations[1] == product_name)

    def prerequisite(self, *args, **kwargs):
        product_name = kwargs.get('product_name')
        return self.navigate_to(
            ProductEntity, 'Edit', entity_name=product_name)

    def step(self, *args, **kwargs):
        self.parent.repositories.click()


@navigator.register(RepositoryEntity, 'New')
class AddNewRepository(NavigateStep):
    """Navigate to Create Product Repository page

    Args:
        product_name: name of product
    """
    VIEW = RepositoryCreateView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All', **kwargs)

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(RepositoryEntity, 'Edit')
class EditRepository(NavigateStep):
    """Navigate to Edit Product Repository page

    Args:
        product_name: name of product
        entity_name: name of repository
    """
    VIEW = RepositoryEditView

    def am_i_here(self, *args, **kwargs):
        prod_name = kwargs.get('product_name')
        repo_name = kwargs.get('entity_name')
        return (
            self.view.is_displayed
            and self.view.breadcrumb.locations[1] == prod_name
            and self.view.breadcrumb.locations[3] == repo_name
        )

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All', **kwargs)

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
