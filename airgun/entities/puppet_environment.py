from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.puppet_environment import (
    ImportPuppetEnvironmentView,
    PuppetEnvironmentCreateView,
    PuppetEnvironmentTableView,
)


class PuppetEnvironmentEntity(BaseEntity):

    def create(self, values):
        """Create puppet environment entity"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def read(self, entity_name):
        """Read puppet environment entity values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values):
        """Update puppet environment values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()

    def delete(self, value):
        """Delete puppet environment entity"""
        view = self.navigate_to(self, 'All')
        view.search(value)
        view.table.row(name=value)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()

    def search(self, value):
        """Search for puppet environment entity"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def import_environments(self, value):
        """Import puppet environments"""
        view = self.navigate_to(self, 'Import')
        view.table.row(environment=value)['Environment'].widget.click()
        view.update.click()


@navigator.register(PuppetEnvironmentEntity, 'All')
class ShowAllPuppetEnvironmentsView(NavigateStep):
    """Navigate to All Puppet Environment screen."""
    VIEW = PuppetEnvironmentTableView

    def step(self, *args, **kwargs):
        self.view.menu.select('Configure', 'Environments')


@navigator.register(PuppetEnvironmentEntity, 'New')
class AddNewPuppetEnvironmentView(NavigateStep):
    """Navigate to Create Puppet Environment screen."""
    VIEW = PuppetEnvironmentCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(PuppetEnvironmentEntity, 'Edit')
class EditPuppetEnvironmentView(NavigateStep):
    """Navigate to Edit Puppet Environment screen.

        Args:
            entity_name: name of puppet environment
    """
    VIEW = PuppetEnvironmentCreateView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(PuppetEnvironmentEntity, 'Import')
class ImportPuppetEnvironmentView(NavigateStep):
    """Navigate to Import Puppet Environment screen."""
    VIEW = ImportPuppetEnvironmentView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.import_environments.click()
