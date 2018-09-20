from widgetastic.widget import (
    Checkbox,
    ConditionalSwitchableView,
    ParametrizedLocator,
    Select,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb, Button

from airgun.views.common import (
    AddRemoveResourcesView,
    BaseLoggedInView,
    SatSecondaryTab,
    SearchableViewMixin,
)
from airgun.widgets import (
    Date,
    EditableEntry,
    RadioGroup,
    SatSelect,
    SatTable,
    Search,
)


class CVFRuleActions(View):
    edit = Text(".//button[contains(@ng-click, 'rule.editMode')]")
    save = Text(".//button[contains(@ng-click, 'handleSave()')]")
    cancel = Text(".//button[contains(@ng-click, 'handleCancel()')]")


class CVFRuleVersion(View):
    rule_type = SatSelect(locator=".//select[@ng-model='rule.type']")
    rule = ConditionalSwitchableView(reference='rule_type')
    version_text = Text(
        ".//span[@ng-hide='rule.editMode']//descendant::span[last()]")

    @rule.register('All Versions')
    class all_versions(View):
        pass

    @rule.register('Equal To')
    class equal_to(View):
        version = TextInput(id='version')

    @rule.register('Greater Than')
    class greater_than(View):
        min_version = TextInput(id='minVersion')

    @rule.register('Less Than')
    class less_than(View):
        max_version = TextInput(id='maxVersion')

    @rule.register('Range')
    class range(View):
        min_version = TextInput(id='minVersion')
        max_version = TextInput(id='maxVersion')

    def fill(self, values):
        # todo: docstring explaining fill needed to support tuple with values
        # which will be properly passed to widgets
        if not isinstance(values, tuple):
            values = (values,)
        was_change = self.rule_type.fill(values[0])
        if len(values) == 1:
            return was_change
        widgets_list = [
            'rule.{}'.format(name) for name in self.rule.widget_names]
        values = dict(zip(widgets_list, values[1:]))
        return super().fill(values) or was_change

    def read(self):
        return self.version_text.read()


class CVFEditableEntry(EditableEntry):
    """Content view filter variant of Editable Entry, main difference of which
    is ``span`` tags instead of ``dd`` and ``dt``.
    """

    def __init__(self, parent, locator=None, name=None, logger=None):
        """Supports initialization via ``locator=`` or ``name=``"""
        if locator and name or not locator and not name:
            raise TypeError('Please specify either locator or name')
        locator = (
            locator or
            ".//span[contains(@class, 'info-label')][normalize-space(.)='{}']"
            "/following-sibling::span[contains(@class, 'info-value')]"
            .format(name)
        )
        super(EditableEntry, self).__init__(parent, locator, logger)


class AffectedRepositoriesTab(SatSecondaryTab):
    """Affected repositories tab contains repositories count inside tab title,
    making it impossible to rely on exact string value. Using ``starts-with``
    instead.
    """

    TAB_LOCATOR = ParametrizedLocator(
        './/nav[@class="ng-scope" or not(@*)]/ul[contains(@class, "nav-tabs")]'
        '/li[./a[starts-with(normalize-space(), {@tab_name|quote})]]'
    )


class ContentViewFiltersView(BaseLoggedInView, SearchableViewMixin):
    breadcrumb = BreadCrumb()

    new_filter = Text(".//button[@ui-sref='content-view.yum.filters.new']")
    remove_selected = Text(".//button[@ng-click='removeFilters()']")

    table = SatTable(
        locator='//table',
        column_widgets={
            0: Checkbox(locator=".//input[@type='checkbox']"),
            'Name': Text('./a'),
        },
    )

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Content Views'
                and self.breadcrumb.read() == 'Yum Filters'
        )


class CreateYumFilterView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    name = TextInput(id='name')
    content_type = Select(id='type')
    inclusion_type = Select(id='inclusion')
    description = TextInput(id='description')

    save = Text('.//button[contains(@ng-click, "handleSave()")]')
    cancel = Text('.//button[@ng-click="handleCancel()"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Content Views'
            and self.breadcrumb.read() == 'Create Yum Filter'
        )


class EditYumFilterView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    filter_type = Text('//header/small')

    content_tabs = ConditionalSwitchableView(reference='filter_type')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and len(self.breadcrumb.locations) > 3
            and self.breadcrumb.locations[2] == 'Yum Filters'
            and self.breadcrumb.read() != 'Create Yum Filter'
        )

    @View.nested
    class details(SatSecondaryTab):
        name = CVFEditableEntry(name='Name')
        description = CVFEditableEntry(name='Description')

    @content_tabs.register(lambda filter_type: filter_type.endswith('RPM'))
    class rpm_filter(View):

        @View.nested
        class rpms(SatSecondaryTab, SearchableViewMixin):
            TAB_NAME = 'RPMs'

            exclude_no_errata = Checkbox(
                locator=".//input[@type='checkbox']"
                        "[@ng-model='filter.original_packages']"
            )
            add_rule = Text(".//button[@ng-click='addRule()']")
            remove_rule = Text(".//button[@ng-click='removeRules(filter)']")
            table = SatTable(
                locator='//table',
                column_widgets={
                    0: Checkbox(locator=".//input[@type='checkbox']"),
                    'RPM Name': TextInput(locator='.//input'),
                    'Architecture': TextInput(locator='.//input'),
                    'Version': CVFRuleVersion(),
                    4: CVFRuleActions(),
                },
            )

    @content_tabs.register(lambda filter_type: filter_type.endswith('Errata'))
    class errata_filter(AddRemoveResourcesView):

        @View.nested
        class AddTab(SatSecondaryTab):
            TAB_NAME = 'Add'
            security = Checkbox(locator=".//input[@ng-model='types.security']")
            enhancement = Checkbox(
                locator=".//input[@ng-model='types.enhancement']")
            bugfix = Checkbox(
                locator=".//input[@ng-model='types.bugfix']")
            date_type = RadioGroup(
                ".//div[label[contains(@class, 'radio-inline')]]")
            start_date = Date(
                locator=".//input[@ng-model='rule.start_date']")
            end_date = Date(
                locator=".//input[@ng-model='rule.end_date']")
            searchbox = Search()
            add_button = Text(
                './/div[@data-block="list-actions"]'
                '//button[contains(@ng-click, "add")]'
            )
            select_all = Checkbox(
                locator=".//table//th[@class='row-select']/input")
            table = SatTable(locator=".//table")

            def search(self, query=None, filters=None):
                if isinstance(filters, dict):
                    for key, value in filters.items():
                        getattr(self, key).fill(value)
                if query:
                    self.searchbox.search(query)
                return self.table.read()

            def add(self, errata_id=None, filters=None):
                self.search(errata_id, filters)
                if errata_id:
                    self.table.row((
                        'Errata ID', errata_id))[0].widget.fill(True)
                else:
                    self.select_all.fill(True)
                self.add_button.click()

            def fill(self, errata_id=None, filters=None):
                self.add(errata_id, filters)

            def read(self):
                return self.table.read()

        @View.nested
        class erratum_date_range(SatSecondaryTab):
            TAB_NAME = 'Erratum Date Range'

            security = Checkbox(locator=".//input[@ng-model='types.security']")
            enhancement = Checkbox(
                locator=".//input[@ng-model='types.enhancement']")
            bugfix = Checkbox(
                locator=".//input[@ng-model='types.bugfix']")
            date_type = RadioGroup(
                ".//div[label[contains(@class, 'radio-inline')]]")
            start_date = Date(
                locator=".//input[@ng-model='rule.start_date']")
            end_date = Date(
                locator=".//input[@ng-model='rule.end_date']")

            save = Text('//button[contains(@ng-click, "handleSave()")]')
            cancel = Text('//button[contains(@ng-click, "handleCancel()")]')

            def after_fill(self, was_change):
                self.save.click()

        def add(self, errata_id=None, filters=None):
            """Assign some resource(s).

            :param str or list values: string containing resource name or a
                list of such strings.
            """
            return self.AddTab.fill(errata_id, filters)

        def read(self):
            """Read all table values from both resource tables"""
            if self.erratum_date_range.is_displayed:
                return {'erratum_date_range': self.erratum_date_range.read()}
            return {
                'assigned': self.ListRemoveTab.read(),
                'unassigned': self.AddTab.read(),
            }

    @content_tabs.register(
        lambda filter_type: filter_type.endswith('Package Groups'))
    class package_group_filter(AddRemoveResourcesView):
        pass

    @View.nested
    class affected_repositories(AffectedRepositoriesTab):
        TAB_NAME = 'Affected Repositories'
        filter_toggle = RadioGroup(".//div[@class='col-sm-8']")
        product_filter = Select(locator=".//select[@ng-model='product']")
        searchbox = TextInput(locator=".//input[@ng-model='repositorySearch']")
        update_repositories = Button('Update Repositories')
        select_all = Checkbox(
            locator=".//table//th[@class='row-select']/input")
        table = SatTable(
            locator='.//table',
            column_widgets={0: Checkbox(locator=".//input[@type='checkbox']")},
        )
