from asyncio import wait_for
import time

from navmazing import NavigateToSibling
from widgetastic.exceptions import NoSuchElementException

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.contentview_new import (
    AddContentViewModal,
    AddRPMRuleView,
    ContentViewCreateView,
    ContentViewEditView,
    ContentViewTableView,
    ContentViewVersionDetailsView,
    ContentViewVersionPromoteView,
    ContentViewVersionPublishView,
    CreateFilterView,
    EditFilterView,
)


class NewContentViewEntity(BaseEntity):
    endpoint_path = '/content_views'

    def create(self, values, composite=False):
        """Create a new content view"""
        view = self.navigate_to(self, 'New')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        if composite:
            view.composite_tile.click()
        view.fill(values)
        view.submit.click()

    def search(self, value):
        """Search for content view"""
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        if not view.table.is_displayed:
            # no table present, no CVs in this Org
            return None
        return view.search(value)

    def publish(self, entity_name, values=None, promote=False, lce=None):
        """Publishes new version of CV, optionally allowing for instant promotion"""
        view = self.navigate_to(self, 'Publish', entity_name=entity_name)
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        if values:
            view.fill(values)
        if promote:
            view.promote.click()
            view.lce_selector.fill({lce: True})
        view.next_button.click()
        view.finish_button.click()
        wait_for(lambda: view.progressbar.is_displayed, timeout=10)
        view.progressbar.wait_for_result()
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        return view.versions.table.read()

    def check_publish_banner(self, cv_name):
        """Check if the needs_publish banner is displayed on the content view index page"""
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        if not view.table.is_displayed:
            # no table present, no CVs in this Org
            return None
        view.search(cv_name)
        view.table[0][6].widget.item_select('Publish')
        view = ContentViewVersionPublishView(self.browser)
        is_displayed = view.publish_alert.is_displayed
        view.cancel_button.click()
        return is_displayed

    def delete(self, entity_name):
        """Deletes the content view by name"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        # click the 'cv-details-action' dropdown, then click 'Delete'
        view.cv_actions.click()
        view.cv_delete.click()
        view.wait_displayed()
        # Remove from environment(s) wizard, if it appears
        if view.next_button.is_displayed:
            view.next_button.click()
            view.delete_finish.click()

    def delete_version(self, entity_name, version):
        """Deletes the specified version of the content view
        :return: bool
        True if specified version was found and clicked 'Delete'
        False (default) if not found in table by version name
        """
        result = False
        view = self.navigate_to(
            self,
            'Version',
            entity_name=entity_name,
            version=version,
            timeout=60,
        )
        time.sleep(5)  # 'Loading' widget on page
        self.browser.plugin.ensure_page_safe(timeout='10s')
        wait_for(lambda: view.table.is_displayed, timeout=20)
        result = view.version_dropdown.item_select('Delete')
        view.wait_displayed()
        # Remove from environment(s) wizard, if it appears
        if view.next_button.is_displayed:
            view.next_button.click()
            view.delete_finish.click()
        return result

    def add_content(self, entity_name, content_name):
        """Add specified content to the given Content View"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        wait_for(lambda: view.repositories.resources.is_displayed, timeout=10)
        view.repositories.resources.add(content_name)
        return view.repositories.resources.read()

    def add_cv(self, ccv_name, cv_name, always_update=False, version=None):
        """Adds selected CV to selected CCV, optionally with support for always_update and specified version"""
        view = self.navigate_to(self, 'Edit', entity_name=ccv_name)
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        view.content_views.resources.add(cv_name)
        view = AddContentViewModal(self.browser)
        if always_update:
            view.always_update.fill(True)
        if version:
            view.version_select.item_select(version)
        view.submit_button.click()
        view = self.navigate_to(self, 'Edit', entity_name=ccv_name)
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        wait_for(lambda: view.content_views.resources.is_displayed, timeout=10)
        return view.content_views.resources.read()

    def read_cv(self, entity_name, version_name):
        """Reads the table for a specified Content View's specified Version"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        view.versions.search(version_name)
        return view.versions.table.row(version=version_name).read()

    def read_repositories(self, entity_name):
        """Reads the repositories table for a specified Content View"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.repositories.resources.read()

    def read_version_table(self, entity_name, version, tab_name, search_param=None):
        """Reads a specific table for a CV Version"""
        view = self.navigate_to(
            self,
            'Version',
            entity_name=entity_name,
            version=version,
            timeout=60,
        )
        time.sleep(5)
        self.browser.plugin.ensure_page_safe(timeout='5s')
        # This allows dynamic access to the proper table
        wait_for(lambda: getattr(view, tab_name).table.wait_displayed(), timeout=10)
        if search_param:
            getattr(view, tab_name).searchbox.search(search_param)
        return getattr(view, tab_name).table.read()

    def create_filter(self, entity_name, filter_name, filter_type, filter_inclusion):
        """Create a new filter on a CV - filter_type should be one of the available dropdown options
        in the Content Type dropdown, and filter_inclusion should be either 'include' or 'exclude'
        :return: dict with new filter table row
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.filters.new_filter.click()
        view = CreateFilterView(self.browser)
        view.name.fill(filter_name)
        view.filterType.fill(filter_type)
        if filter_inclusion == 'include':
            view.includeFilter.fill(True)
        elif filter_inclusion == 'exclude':
            view.excludeFilter.fill(True)
        else:
            raise ValueError("Filter_inclusion must be one of include or exclude.")
        view.create.click()
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.filters.table.read()

    def delete_filter(self, entity_name, filter_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.filters.search(filter_name)
        view.filters.table[0][6].widget.item_select('Remove')
        # Attempt to read the table, and if there isn't one return True, else delete failed so return False
        try:
            view.filters.table.read()
        except NoSuchElementException:
            return True
        else:
            return False

    """
    Filter Editing will be handled in discrete methods, since each type has different actions. These will be
    created as tests and cases are encountered.
    """

    def add_rule_rpm_filter(self, entity_name, filter_name, rpm_name, arch):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.filters.search(filter_name)
        view.filters.table[0][1].widget.click()
        view = EditFilterView(self.browser)
        view.addRpmRule.click()
        view = AddRPMRuleView(self.browser)
        view.rpmName.fill(rpm_name)
        view.architecture.fill(arch)
        view.addEdit.click()
        view = EditFilterView(self.browser)
        return view.rpmRuleTable.read()

    def add_rule_tag_filter(self, entity_name, filter_name, rpm_name, arch):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.filters.search(filter_name)
        view.filters.table[0][1].widget.click()
        view = EditFilterView(self.browser)
        view.addRpmRule.click()
        view = AddRPMRuleView(self.browser)
        view.rpmName.fill(rpm_name)
        view.architecture.fill(arch)
        view.addEdit.click()
        view = EditFilterView(self.browser)
        return view.rpmRuleTable.read()

    def read_french_lang_cv(self):
        """Navigates to main CV page, when system is set to French, and reads table"""
        view = self.navigate_to(self, 'French')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        return view.table.read()

    def promote(self, entity_name, version_name, lce_name):
        """Promotes the selected version of content view to given environment.
        :return: dict with new content view version table row; contains keys
        like 'Version', 'Status', 'Environments' etc.
        """
        view = self.navigate_to(self, 'Promote', entity_name=entity_name, version_name=version_name)
        modal = ContentViewVersionPromoteView(self.browser)
        if modal.is_displayed:
            modal.lce.fill({lce_name: True})
            modal.promote_btn.click()
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.versions.search(version_name)
        return view.versions.table.row(version=version_name).read()

    def update(self, entity_name, values):
        """Update existing content view"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        time.sleep(3)
        filled_values = view.fill(values)
        view.flash.assert_no_error()
        view.flash.dismiss()
        return filled_values


@navigator.register(NewContentViewEntity, 'All')
class ShowAllContentViewsScreen(NavigateStep):
    """Navigate to All Content Views screen."""

    VIEW = ContentViewTableView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Lifecycle', 'Content Views')


@navigator.register(NewContentViewEntity, 'French')
class ShowAllContentViewsScreenFrench(NavigateStep):
    """Navigate to All Content Views screen ( in French )"""

    VIEW = ContentViewTableView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Contenu', 'Lifecycle', 'Content Views')


@navigator.register(NewContentViewEntity, 'New')
class CreateContentView(NavigateStep):
    """Navigate to Create content view."""

    VIEW = ContentViewCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.create_content_view.click()


@navigator.register(NewContentViewEntity, 'Edit')
class EditContentView(NavigateStep):
    """Navigate to Edit Content View screen."""

    VIEW = ContentViewEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(NewContentViewEntity, 'Version')
class ShowContentViewVersionDetails(NavigateStep):
    """Navigate to Content View Version screen for a specific Version."""

    VIEW = ContentViewVersionDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'Edit', **kwargs)

    def step(self, *args, **kwargs):
        version = kwargs.get('version')
        self.parent.versions.wait_displayed()
        self.parent.versions.search(version)
        self.parent.versions.table.wait_displayed()
        self.parent.versions.table.row(version=version)['Version'].widget.click()


@navigator.register(NewContentViewEntity, 'Publish')
class PublishContentViewVersion(NavigateStep):
    """Navigate to Content View Publish screen.
    Args:
        entity_name: name of content view
    """

    VIEW = ContentViewVersionPublishView

    def prerequisite(self, *args, **kwargs):
        """Open Content View first."""
        return self.navigate_to(self.obj, 'Edit', entity_name=kwargs.get('entity_name'), timeout=20)

    def step(self, *args, **kwargs):
        """Click 'Publish new version' button"""
        self.parent.publish.wait_displayed()
        self.parent.publish.click()


@navigator.register(NewContentViewEntity, 'Promote')
class PromoteContentViewVersion(NavigateStep):
    """Navigate to Content View Promote screen.
    Args:
        entity_name: name of content view
        version_name: name of content view version to promote
    """

    VIEW = ContentViewEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'Edit', entity_name=kwargs.get('entity_name'))

    def step(self, *args, **kwargs):
        version_name = kwargs.get('version_name')
        self.parent.versions.wait_displayed()
        self.parent.versions.search(version_name)
        self.parent.version.table.wait_displayed()
        self.parent.versions.table[0][7].widget.item_select('Promote')
