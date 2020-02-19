from widgetastic.widget import Checkbox
from widgetastic.widget import Select
from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView
from airgun.views.common import ReadOnlyEntry
from airgun.views.common import SatTab
from airgun.views.common import SatTable
from airgun.widgets import ItemsListReadOnly
from airgun.widgets import Search


class PackagesView(BaseLoggedInView):
    """Main Packages view"""
    title = Text("//h2[contains(., 'Packages')]")
    table = SatTable('.//table', column_widgets={'RPM': Text("./a")})

    repository = Select(locator=".//select[@ng-model='repository']")
    applicable = Checkbox(locator=".//input[@ng-model='showApplicable']")
    upgradable = Checkbox(locator=".//input[@ng-model='showUpgradable']")
    search_box = Search()

    def search(self, query, repository='All Repositories', applicable=False,
               upgradable=False):
        """Perform search using search box on the page and return table
        contents.

        :param str query: search query to type into search field. E.g.
            ``name = "bar"``.
        :param str repository: repository name to select when searching for the
            package.
        :param bool applicable: To show only applicable packages
        :param bool upgradable: To show only upgradable packages
        :return: list of dicts representing table rows
        :rtype: list
        """
        self.repository.fill(repository)
        # set the upgradable first as if enabled, applicable element will be
        # disabled
        self.upgradable.fill(upgradable)
        if not upgradable:
            self.applicable.fill(applicable)
        self.search_box.search(query)
        return self.table.read()

    @property
    def is_displayed(self):
        """The view is displayed when it's title exists"""
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class PackageDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)

        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Packages'
        )

    @View.nested
    class details(SatTab):
        # Package Information:
        installed_on = ReadOnlyEntry(name='Installed On')
        applicable_to = ReadOnlyEntry(name='Applicable To')
        upgradable_for = ReadOnlyEntry(name='Upgradable For')
        description = ReadOnlyEntry(name='Description')
        summary = ReadOnlyEntry(name='Summary')
        group = ReadOnlyEntry(name='Group')
        license = ReadOnlyEntry(name='License')
        url = ReadOnlyEntry(name='Url')
        # File Information:
        size = ReadOnlyEntry(name='Size')
        filename = ReadOnlyEntry(name='Filename')
        checksum = ReadOnlyEntry(name='Checksum')
        checksum_type = ReadOnlyEntry(name='Checksum Type')
        # Build Information:
        source_rpm = ReadOnlyEntry(name='Source RPM')
        build_host = ReadOnlyEntry(name='Build Host')
        build_time = ReadOnlyEntry(name='Build Time')

    @View.nested
    class files(SatTab):
        package_files = ItemsListReadOnly(
            locator=".//div[@data-block='content']//ul")
