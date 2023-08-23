import re

from widgetastic.widget import Checkbox, Text, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SatTab, TaskDetailsView
from airgun.widgets import ItemsList, ReadOnlyEntry, SatSelect, SatTable, Search


class ErratumView(BaseLoggedInView):
    title = Text("//h1[contains(., 'Errata')]")
    table = SatTable(
        locator='.//table',
        column_widgets={
            0: Checkbox(locator=".//input[@type='checkbox']"),
            'Errata ID': Text("./a"),
        },
    )
    repo_filter = SatSelect(".//select[@ng-model='repository']")
    applicable_filter = Checkbox(locator=".//input[@ng-model='showApplicable']")
    installable_filter = Checkbox(locator=".//input[@ng-model='showInstallable']")
    apply_errata = Text(".//button[contains(@class, 'btn-primary')][@ng-click='goToNextStep()']")
    searchbox = Search()

    def search(self, query, applicable=True, installable=False, repo=None):
        """Apply available filters before proceeding with searching and
        automatically set proper search mask if errata id instead of errata
        title was passed.

        :param str query: search query to type into search field. Both errata
            id (RHEA-2012:0055) and errata title (Sea_Erratum) are supported.
        :param bool applicable: filter by only applicable errata
        :param bool installable: filter by only installable errata
        :param str optional repo: filter by repository name
        :return: list of dicts representing table rows
        :rtype: list
        """
        self.installable_filter.fill(installable)
        self.applicable_filter.fill(applicable)
        if repo is not None:
            self.repo_filter.fill(repo)

        if re.search(r'\w{3,4}[:-]\d{4}[-:]\d{4}', query):
            query = f'id = {query}'
        self.searchbox.search(query)

        return self.table.read()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ErrataDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    @View.nested
    class details(SatTab):
        advisory = ReadOnlyEntry(name='Advisory')
        cves = ReadOnlyEntry(name='CVEs')
        type = ReadOnlyEntry(name='Type')
        severity = ReadOnlyEntry(name='Severity')
        issued = ReadOnlyEntry(name='Issued')
        last_updated_on = ReadOnlyEntry(name='Last Updated On')
        reboot_suggested = ReadOnlyEntry(name='Reboot Suggested?')
        topic = Text(
            ".//h3[contains(., 'Topic')]"
            "/following-sibling::p[contains(@class, 'info-paragraph')][1]"
        )
        description = Text(
            ".//h3[contains(., 'Description')]"
            "/following-sibling::p[contains(@class, 'info-paragraph')][1]"
        )
        solution = Text(
            ".//h3[contains(., 'Solution')]"
            "/following-sibling::p[contains(@class, 'info-paragraph')][1]"
        )

    @View.nested
    class content_hosts(SatTab):
        TAB_NAME = 'Content Hosts'
        environment_filter = SatSelect(".//select[@ng-model='environmentFilter']")
        searchbox = Search()
        apply = Text(".//button[@ng-click='goToNextStep()']")
        table = SatTable(
            locator=".//table",
            column_widgets={
                0: Checkbox(locator="./input[@type='checkbox']"),
                'Name': Text("./a"),
            },
        )

        def search(self, query, environment=None):
            """Apply environment filter before proceeding with searching.

            :param str query: search query to type into search field.
            :param str optional environment: filter by environment name
            :return: list of dicts representing table rows
            :rtype: list
            """
            if environment:
                self.environment_filter.fill(environment)
            self.searchbox.search(query)
            return self.table.read()

    @View.nested
    class repositories(SatTab):
        lce_filter = SatSelect(".//select[@ng-model='environmentFilter']")
        cv_filter = SatSelect(".//select[@ng-model='contentViewFilter']")
        searchbox = Search()
        table = SatTable(
            locator=".//table",
            column_widgets={
                'Name': Text("./a"),
                'Product': Text("./a"),
            },
        )

        def search(self, query, lce=None, cv=None):
            """Apply available filters before proceeding with searching.

            :param str query: search query to type into search field.
            :param str optional lce: filter by lifecycle environment name
            :param str optional cv: filter by content view name
            :return: list of dicts representing table rows
            :rtype: list
            """
            if lce:
                self.lce_filter.fill(lce)
            if cv:
                self.cv_filter.fill(cv)
            self.searchbox.search(query)
            return self.table.read()

    @View.nested
    class packages(SatTab):
        independent_packages = ItemsList(
            ".//h3[contains(., 'Independent Packages')]/following-sibling::ul"
        )
        module_stream_packages = ItemsList(
            ".//h3[contains(., 'Module Stream Packages')]/following-sibling::ul"
        )

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Errata'
            and len(self.breadcrumb.locations) > 1
        )


class ApplyErrataView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    environment_filter = SatSelect(".//select[@ng-model='environmentFilter']")
    searchbox = Search()
    next_button = Text(".//button[@ng-click='goToNextStep()']")
    table = SatTable(
        locator=".//table",
        column_widgets={
            0: Checkbox(locator="./input[@type='checkbox']"),
            'Name': Text("./a"),
        },
    )

    def search(self, query, environment=None):
        """Apply environment filter before proceeding with searching.

        :param str query: search query to type into search field.
        :param str optional environment: filter by environment name
        :return: list of dicts representing table rows
        :rtype: list
        """
        if environment:
            self.environment_filter.fill(environment)
        self.searchbox.search(query)
        return self.table.read()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Errata'
            and self.breadcrumb.read() == 'Select Content Host(s)'
        )


class ErrataInstallationConfirmationView(BaseLoggedInView):
    cancel = Text(".//button[@ng-click='transitionBack()']")
    confirm = Text(".//button[@type='submit']")


class ErrataTaskDetailsView(TaskDetailsView):
    BREADCRUMB_LENGTH = 2

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Errata'
            and len(self.breadcrumb.locations) > self.BREADCRUMB_LENGTH
        )
