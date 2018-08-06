
from widgetastic.widget import Checkbox, Select, Text, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import (
    BaseLoggedInView,
    ReadOnlyEntry,
    SatTab,
    SatTable,
    SearchableViewMixin,
)
from airgun.widgets import ItemsList


class SearchablePackageViewMixin(SearchableViewMixin):
    """Packages search widget"""
    repository = Select(locator=".//select[@ng-model='repository']")
    applicable = Checkbox(locator=".//input[@ng-model='showApplicable']")
    upgradable = Checkbox(locator=".//input[@ng-model='showUpgradable']")

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
        # set the upgradable first as if enabled applicable element will be
        # disabled
        self.upgradable.fill(upgradable)
        if not upgradable:
            self.applicable.fill(applicable)

        return super(SearchablePackageViewMixin, self).search(query)


class PackagesView(BaseLoggedInView, SearchablePackageViewMixin):
    """Main Packages view"""
    title = Text("//h2[contains(., 'Packages')]")
    table = SatTable('.//table', column_widgets={'RPM': Text("./a")})

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
        applicable_to = ReadOnlyEntry(name='Applicable To')
        build_host = ReadOnlyEntry(name='Build Host')
        build_time = ReadOnlyEntry(name='Build Time')
        description = ReadOnlyEntry(name='Description')
        checksum = ReadOnlyEntry(name='Checksum')
        checksum_type = ReadOnlyEntry(name='Checksum Type')
        filename = ReadOnlyEntry(name='Filename')
        group = ReadOnlyEntry(name='Group')
        installed_on = ReadOnlyEntry(name='Installed On')
        license = ReadOnlyEntry(name='License')
        size = ReadOnlyEntry(name='Size')
        source_rpm = ReadOnlyEntry(name='Source RPM')
        summary = ReadOnlyEntry(name='Summary')
        upgradable_for = ReadOnlyEntry(name='Upgradable For')
        url = ReadOnlyEntry(name='Url')

    @View.nested
    class files(SatTab):
        package_files = ItemsList(locator=".//div[@data-block='content']//ul")
