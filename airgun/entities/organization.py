from navmazing import NavigateToSibling
from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.common import BaseLoggedInView, WrongContextAlert
from airgun.views.organization import (
    OrganizationCreateView,
    OrganizationEditView,
    OrganizationsView,
    SelectOrganizationContextView,
)


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
    ELLIPSIS_LENGTH = 30

    def am_i_here(self, *args, **kwargs):
        org_name = kwargs.get('org_name')
        if len(org_name) > self.ELLIPSIS_LENGTH:
            org_name = org_name[: self.ELLIPSIS_LENGTH - 3] + '...'
        return org_name == self.view.taxonomies.current_org

    def step(self, *args, **kwargs):
        org_name = kwargs.get('org_name')
        if not org_name:
            raise ValueError('Specify proper value for org_name parameter')
        self.view.taxonomies.select_org(org_name)

    def post_navigate(self, _tries, *args, **kwargs):
        """Handle alert screen and 'Select an Organization' page if present"""
        # Handle WrongContextAlert
        wrong_context_view = WrongContextAlert(self.view.browser)
        if wrong_context_view.is_displayed:
            wrong_context_view.back.click()
            self.view.browser.wait_for_element(
                self.view.menu, exception=False, ensure_page_safe=True
            )

        # Handle 'Select an Organization' page
        # This appears when navigating to org-specific pages from 'Any Organization' context
        set_org_view = SelectOrganizationContextView(self.view.browser)
        if set_org_view.is_displayed:
            self._handle_set_organization_page(set_org_view, *args, **kwargs)

        super().post_navigate(_tries, *args, **kwargs)

    def _handle_set_organization_page(self, set_org_view, *args, **kwargs):
        """Handle the 'Select an Organization' PF5 page using the view.

        This method handles the organization selection page introduced in
        Katello PR #11734 (SetOrganization PF3 to PF5 migration).

        Args:
            set_org_view: Instance of SelectOrganizationContextView
            *args: Additional positional arguments
            **kwargs: Keyword arguments including 'org_name'
        """
        org_name = kwargs.get('org_name')

        # Wait for page title to be visible
        wait_for(
            lambda: set_org_view.title.is_displayed,
            timeout=10,
            delay=0.5,
            message='Waiting for SetOrganization page title',
        )

        # Select organization using widgetastic Select widget
        set_org_view.organization_select.fill(org_name)

        # Wait for Submit button to become enabled
        wait_for(
            lambda: set_org_view.submit_button.is_enabled,
            timeout=10,
            delay=0.5,
            message='Waiting for Submit button to be enabled',
        )

        # Click the Submit button
        set_org_view.submit_button.click()

        # Wait for navigation to complete
        set_org_view.browser.plugin.ensure_page_safe(timeout=30)
