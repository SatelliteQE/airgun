from airgun.entities.base import BaseEntity
from airgun.entities.contentview import ContentViewEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.contentviewfilter import (
    ContentViewFiltersView,
    CreateYumFilterView,
    EditYumFilterView,
)


class ContentViewFilterEntity(BaseEntity):

    def create(self, cv_name, values):
        """Create a new content view filter"""
        view = self.navigate_to(self, 'New', cv_name=cv_name)
        view.fill(values)
        view.save.click()

    def delete(self, cv_name, filter_name):
        """Delete existing content view filter"""
        view = self.navigate_to(self, 'All', cv_name=cv_name)
        view.search(filter_name)
        view.table.row(name=filter_name)[0].widget.fill(True)
        view.remove_selected.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, cv_name, value):
        """Search for content view filter"""
        view = self.navigate_to(self, 'All', cv_name=cv_name)
        return view.search(value)

    def read(self, cv_name, filter_name):
        """Read content view filter values"""
        view = self.navigate_to(
            self, 'Edit',
            cv_name=cv_name,
            filter_name=filter_name,
        )
        return view.read()

    def add_package(
            self, cv_name, filter_name, rpm_name, architecture, version):
        """Add package rule to RPM content view filter.

        :param str cv_name: content view name
        :param str filter_name: content view filter name
        :param str rpm_name: affected package (RPM) name
        :param str architecture: affected architecture
        :param tuple version: tuple containing version values according to UI
            (e.g. ('Equal To', '5.21-1') or ('Range', '4.1', '4.6')
        """
        view = self.navigate_to(
            self, 'Edit',
            cv_name=cv_name,
            filter_name=filter_name,
        )
        view.content_tabs.rpms.add_rule.click()
        view.content_tabs.rpms.table.fill([{
            'RPM Name': rpm_name,
            'Architecture': architecture,
            'Version': version,
        }])
        view.content_tabs.rpms.table[0][4].widget.save.click()
        view.flash.assert_no_error()
        view.flash.dismiss()
        # refresh as otherwise it won't be possible to read values from table
        view.browser.refresh()

    def update_package(self, cv_name, filter_name, rpm_name, new_values,
                       architecture=None, version=None):
        """Update package rule of RPM content view filter.

        :param str cv_name: content view name
        :param str filter_name: content view filter name
        :param str rpm_name: existing package (RPM) name
        :param dict new_values: dictionary with new values where keys are the
            same as column names on UI: 'RPM Name', 'Architecture', 'Version'.
        :param str optional architecture: filter package rule by its
            architecture
        :param str optional version: filter package rule by its version (string
            value with exact correspondence to UI)
        """
        view = self.navigate_to(
            self, 'Edit',
            cv_name=cv_name,
            filter_name=filter_name,
        )
        # form a dict of passed details of rpm filter
        passed_details = {
            'RPM Name': rpm_name,
            'Architecture': architecture,
            'Version': version,
        }

        def row_matches(row, **filters):
            """Returns True if row matches all passed filters"""
            row_values = row.read()
            return all(
                row_values[key] == value
                for key, value in filters.items()
                if value is not None
            )

        # find row which matches all filters
        rows = [
            row for row
            in view.content_tabs.rpms.table.rows()
            if row_matches(row, **passed_details)
        ]
        assert rows, 'Table Row not found using passed filters {}'.format(
            passed_details)
        row = rows[0]
        row[4].widget.edit.click()
        # prepare list with empty values for all preceding rows as it's
        # impossible to fill specific table row, only in proper order
        values = [{} for _ in range(row.index)]
        values.append(new_values)
        view.content_tabs.rpms.table.fill(values)
        row[4].widget.save.click()
        view.flash.assert_no_error()
        view.flash.dismiss()
        # refresh as otherwise it won't be possible to read values from table
        view.browser.refresh()

    def add_errata(
            self, cv_name, filter_name, errata_id=None, search_filters=None):
        """Add errata to errata content view filter.

        :param str cv_name: content view name
        :param str filter_name: content view filter name
        :param str optional errata_id: errata ID. If not provided - all
            available will be added instead (taking into consideration applied
            search filters)
        :param dict search_filters: search filters to apply before adding
            errata. Dictionary where keys are widget names and values are
            widget values accordingly
        """
        view = self.navigate_to(
            self, 'Edit',
            cv_name=cv_name,
            filter_name=filter_name,
        )
        view.content_tabs.add(errata_id, search_filters)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def add_package_group(
            self, cv_name, filter_name, package_group):
        """Add package group to package group content view filter.

        :param str cv_name: content view name
        :param str filter_name: content view filter name
        :param str package_group: package group name
        """
        view = self.navigate_to(
            self, 'Edit',
            cv_name=cv_name,
            filter_name=filter_name,
        )
        view.content_tabs.add(package_group)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search_package(self, cv_name, filter_name, query):
        """Search for specific package in RPM content view filter.

        :param str cv_name: content view name
        :param str filter_name: content view filter name
        :param str query: search query
        """
        view = self.navigate_to(
            self, 'Edit',
            cv_name=cv_name,
            filter_name=filter_name,
        )
        return view.content_tabs.rpms.search(query)

    def update(self, cv_name, filter_name, values):
        """Update content view filter.

        :param str cv_name: content view name
        :param str filter_name: content view filter name
        :param dict values: dictionary with new values
        """
        view = self.navigate_to(
            self, 'Edit',
            cv_name=cv_name,
            filter_name=filter_name,
        )
        view.fill(values)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def update_repositories(self, cv_name, filter_name, repositories=None):
        """Update affected by content view filter repositories.

        :param str cv_name: content view name
        :param str filter_name: content view filter name
        :param list optional repositories: list of affected repositories. If
            not provided - all repositories will be affected.
        """
        view = self.navigate_to(
            self, 'Edit',
            cv_name=cv_name,
            filter_name=filter_name,
        )
        if not repositories:
            view.affected_repositories.filter_toggle.fill(
                'This filter applies to all repositories in the content view '
                '(current and future).'
            )
            return
        view.affected_repositories.filter_toggle.fill(
            'This filter applies only to a subset of repositories in the '
            'content view.'
        )
        # deselect all repositories
        view.affected_repositories.select_all.fill(True)
        view.affected_repositories.select_all.fill(False)
        for repo in repositories:
            view.affected_repositories.searchbox.fill(repo)
            view.affected_repositories.table.row(
                name=repo)[0].widget.fill(True)
        view.affected_repositories.update_repositories.click()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(ContentViewFilterEntity, 'All')
class ShowAllContentViewFilters(NavigateStep):
    """Navigate to All Content View Filters screen by proceeding through
    Content View -> Yum Content -> Filters tab.

    Args:
        cv_name: name of content view
    """
    VIEW = ContentViewFiltersView

    def am_i_here(self, *args, **kwargs):
        cv_name = kwargs.get('cv_name')
        return (
                self.view.is_displayed
                and self.view.breadcrumb.locations[1] == cv_name)

    def prerequisite(self, *args, **kwargs):
        cv_name = kwargs.get('cv_name')
        return self.navigate_to(
            ContentViewEntity, 'Edit', entity_name=cv_name)

    def step(self, *args, **kwargs):
        self.parent.filters.select()


@navigator.register(ContentViewFilterEntity, 'New')
class AddNewContentViewFilter(NavigateStep):
    """Navigate to New Content View Filter screen.

    Args:
        cv_name: name of content view
    """
    VIEW = CreateYumFilterView

    def am_i_here(self, *args, **kwargs):
        cv_name = kwargs.get('cv_name')
        return (
                self.view.is_displayed
                and self.view.breadcrumb.locations[1] == cv_name)

    def prerequisite(self, *args, **kwargs):
        cv_name = kwargs.get('cv_name')
        return self.navigate_to(self.obj, 'All', cv_name=cv_name)

    def step(self, *args, **kwargs):
        self.parent.new_filter.click()


@navigator.register(ContentViewFilterEntity, 'Edit')
class EditContentView(NavigateStep):
    """Navigate to Edit Content View Filter screen.

    Args:
        cv_name: name of content view
        filter_name: name of content view filter
    """
    VIEW = EditYumFilterView

    def am_i_here(self, *args, **kwargs):
        cv_name = kwargs.get('cv_name')
        filter_name = kwargs.get('filter_name')
        return (
                self.view.is_displayed
                and self.view.breadcrumb.locations[1] == cv_name
                # depending on tab both 'filter' and 'Edit filter' may occur
                and filter_name in self.view.breadcrumb.locations[3])

    def prerequisite(self, *args, **kwargs):
        cv_name = kwargs.get('cv_name')
        return self.navigate_to(self.obj, 'All', cv_name=cv_name)

    def step(self, *args, **kwargs):
        filter_name = kwargs.get('filter_name')
        self.parent.search(filter_name)
        self.parent.table.row(name=filter_name)['Name'].widget.click()
