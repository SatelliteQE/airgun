from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.utils import retry_navigation
from airgun.views.common import BaseLoggedInView
from airgun.views.common import WrongContextAlert
from airgun.views.organization import OrganizationCreateView
from airgun.views.organization import OrganizationEditView
from airgun.views.organization import OrganizationsView


class OrganizationEntity(BaseEntity):
    endpoint_path = '/organizations'

    def create(self, values):
        """Create new organization entity"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete existing organization"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def read(self, entity_name, widget_names=None):
        """Read specific organization details"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def search(self, value):
        """Search for organization entity"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def update(self, entity_name, values):
        """Update necessary values for organization"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def select(self, org_name):
        """Select necessary organization from context menu on the top of the page"""
        self.navigate_to(self, 'Context', org_name=org_name)


@navigator.register(OrganizationEntity, 'All')
class ShowAllOrganizations(NavigateStep):
    """Navigate to All Organizations page"""

    VIEW = OrganizationsView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'Organizations')


@navigator.register(OrganizationEntity, 'New')
class AddNewOrganization(NavigateStep):
    """Navigate to Create Organization page"""

    VIEW = OrganizationCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)


@navigator.register(OrganizationEntity, 'Edit')
class EditOrganization(NavigateStep):
    """Navigate to Edit Organization page

    Args:
        entity_name: name of the organization
    """

    VIEW = OrganizationEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(OrganizationEntity, 'Context')
class SelectOrganizationContext(NavigateStep):
    """Select Organization from menu

    Args:
        org_name: name of the organization
    """

    VIEW = BaseLoggedInView

    def am_i_here(self, *args, **kwargs):
        org_name = kwargs.get('org_name')
        if len(org_name) > 30:
            org_name = org_name[:27] + '...'
        return org_name == self.view.taxonomies.current_org

    def step(self, *args, **kwargs):
        org_name = kwargs.get('org_name')
        if not org_name:
            raise ValueError('Specify proper value for org_name parameter')
        self.view.taxonomies.select_org(org_name)

    def post_navigate(self, _tries, *args, **kwargs):
        """Handle alert screen if it's present"""
        wrong_context_view = WrongContextAlert(self.view.browser)
        if wrong_context_view.is_displayed:
            wrong_context_view.back.click()
            self.view.browser.wait_for_element(
                self.view.menu, exception=False, ensure_page_safe=True
            )
        super().post_navigate(_tries, *args, **kwargs)
