from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.common import BaseLoggedInView

from airgun.views.organization import (
    OrganizationCreateView,
    OrganizationEditView,
    OrganizationsView
)


class OrganizationEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def read(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def update(self, entity_name, values):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def select(self, org_name):
        self.navigate_to(self, 'Context', org_name=org_name)


@navigator.register(OrganizationEntity, 'All')
class ShowAllOrganizations(NavigateStep):
    VIEW = OrganizationsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'Organizations')


@navigator.register(OrganizationEntity, 'New')
class AddNewOrganization(NavigateStep):
    VIEW = OrganizationCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)


@navigator.register(OrganizationEntity, 'Edit')
class EditOrganization(NavigateStep):
    VIEW = OrganizationEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(OrganizationEntity, 'Context')
class SelectOrganizationContext(NavigateStep):
    VIEW = BaseLoggedInView

    def am_i_here(self, *args, **kwargs):
        org_name = kwargs.get('org_name')
        current_org = self.view.taxonomies.current_org()
        if len(org_name) > 30:
            org_name = org_name[:27] + '...'
        return current_org == org_name

    def step(self, *args, **kwargs):
        org_name = kwargs.get('org_name')
        if not org_name:
            raise ValueError('Specify proper value for org_name parameter')
        self.view.taxonomies.select_org(org_name)
