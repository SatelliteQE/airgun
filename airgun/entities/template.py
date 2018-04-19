from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.template import (
    ProvisioningTemplateDetailsView,
    ProvisioningTemplateView,
)


class ProvisioningTemplateEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def clone(self, entity_name, values):
        view = self.navigate_to(self, 'Clone', entity_name=entity_name)
        view.fill(values)
        view.submit.click()


@navigator.register(ProvisioningTemplateEntity, 'All')
class ShowAllTemplates(NavigateStep):
    VIEW = ProvisioningTemplateView

    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Provisioning Templates')


@navigator.register(ProvisioningTemplateEntity, 'New')
class AddNewTemplate(NavigateStep):
    VIEW = ProvisioningTemplateDetailsView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)


@navigator.register(ProvisioningTemplateEntity, 'Edit')
class EditTemplate(NavigateStep):
    VIEW = ProvisioningTemplateDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.search(kwargs.get('entity_name'))
        self.parent.edit.click()


@navigator.register(ProvisioningTemplateEntity, 'Clone')
class CloneTemplate(NavigateStep):
    VIEW = ProvisioningTemplateDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.search(kwargs.get('entity_name'))
        self.parent.clone.click()
