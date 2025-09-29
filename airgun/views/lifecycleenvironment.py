from widgetastic.widget import (
    ParametrizedLocator,
    ParametrizedView,
    Table,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb, Button

from airgun.views.common import BaseLoggedInView, SatTab, SearchableViewMixin
from airgun.widgets import (
    EditableEntry,
    EditableEntryCheckbox,
    ReadOnlyEntry,
    SatSelect,
    Search,
)


class LCEView(BaseLoggedInView, ParametrizedView):
    title = Text("//h2[contains(., 'Lifecycle Environment Paths')]")
    new_path = Text(
        "//a[contains(@href, '/lifecycle_environments') "
        "and contains(@href, 'new') and contains(@class, 'btn-primary')]"
    )
    edit_parent_env = Text(
        "//table[contains(@class, 'info-blocks')]//a[contains(@ui-sref, 'environment.details')]"
    )
    parent_env_cvs_count = Text(
        "//table[contains(@class, 'info-blocks')]//td[span[contains(., 'Content Views')]]/div"
    )
    parent_env_products_count = Text(
        "//table[contains(@class, 'info-blocks')]//td[span[contains(., 'Products')]]/div"
    )
    parent_env_products_errata = Text(
        "//table[contains(@class, 'info-blocks')]//td[span[contains(., 'Errata')]]/div"
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None

    @View.nested
    class lce(ParametrizedView):
        """Parametrized view for the lifecycle environement, takes an LCE name on instantiation"""

        ROOT = ParametrizedLocator(
            ".//div[@ng-repeat='path in paths'][table//th/a[normalize-space(.)='{lce_name}']]"
        )
        PARAMETERS = ("lce_name",)
        LAST_ENV = "//div[@ng-repeat='path in paths']//table//th[last()]"
        current_env = Text(ParametrizedLocator(".//a[normalize-space(.)='{lce_name}']"))
        envs_table = Table(locator=".//table")
        new_child = Text(".//a[contains(@href, '/lifecycle_environments/')]")

        @classmethod
        def all(cls, browser):
            """Helper method which returns list of tuples with all available
            LCE names (last available environment is used as a name). It's
            required for :meth:`read` to work properly.
            """
            return [(element.text,) for element in browser.elements(cls.LAST_ENV)]

        def read(self):
            """Returns content views and count hosts count per each available
            lifecycle environment
            We get dictionary in next format::

                {
                    'LCE_1': {'Content Views': 0, 'Content Hosts': 1},
                    'LCE_2': {'Content Views': 1, 'Content Hosts': 2},
                }

            """
            result = {}
            available_envs = self.envs_table.headers[1:]
            lce_metric_names = [row[0].text for row in self.envs_table]
            for column_name in available_envs:
                metric_values = (int(row[column_name].text) for row in self.envs_table)
                result[column_name] = {}
                for row_name in lce_metric_names:
                    result[column_name][row_name] = next(metric_values)
            return result


class LCECreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id="name")
    label = TextInput(id="label")
    description = TextInput(id="description")
    submit = Text("//button[contains(@ng-click, 'handleSave')]")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False
        )
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == "Environments List"
            and self.breadcrumb.read() == "New Environment"
        )


class LCEEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    remove = Button("Remove Environment")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False
        )
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == "Environments"
            and self.breadcrumb.read() != "New Environment"
        )

    @View.nested
    class details(SatTab):
        name = EditableEntry(name="Name")
        label = ReadOnlyEntry(name="Label")
        description = EditableEntry(name="Description")
        unauthenticated_pull = EditableEntryCheckbox(name="Unauthenticated Pull")
        registry_name_pattern = EditableEntry(name="Registry Name Pattern")

    @View.nested
    class content_views(SatTab, SearchableViewMixin):
        TAB_NAME = "Content Views"
        resources = Table(locator=".//table")

    @View.nested
    class packages(SatTab):
        cv_filter = SatSelect(".//select[@ng-model='contentView']")
        repo_filter = SatSelect(".//select[@ng-model='repository']")
        searchbox = Search()
        table = Table(locator=".//table")

        def search(self, query, cv=None, repo=None):
            """Apply available filters before proceeding with searching.

            :param str query: search query to type into search field.
            :param str optional cv: filter by content view name
            :param str optional repo: filter by repository name
            :return: list of dicts representing table rows
            :rtype: list
            """
            if cv:
                self.cv_filter.fill(cv)
            if repo:
                self.repo_filter.fill(repo)
            self.searchbox.search(query)
            return self.table.read()

    @View.nested
    class module_streams(SatTab):
        TAB_NAME = "Module Streams"

        cv_filter = SatSelect(".//select[@ng-model='contentView']")
        repo_filter = SatSelect(".//select[@ng-model='repository']")
        searchbox = Search()
        table = Table(".//table")

        def search(self, query, cv=None, repo=None):
            """Apply available filters before proceeding with searching.

            :param str query: search query to type into search field.
            :param str optional cv: filter by content view name
            :param str optional repo: filter by repository name
            :return: list of dicts representing table rows
            :rtype: list
            """
            if cv:
                self.cv_filter.fill(cv)
            if repo:
                self.repo_filter.fill(repo)
            self.searchbox.search(query)
            return self.table.read()
