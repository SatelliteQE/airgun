from widgetastic.widget import Checkbox
from widgetastic.widget import ConditionalSwitchableView
from widgetastic.widget import ParametrizedLocator
from widgetastic.widget import Select
from widgetastic.widget import Table
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly import Button

from airgun.views.common import AddRemoveResourcesView
from airgun.views.common import AddTab
from airgun.views.common import BaseLoggedInView
from airgun.views.common import SatSecondaryTab
from airgun.views.common import SearchableViewMixin
from airgun.widgets import DatePickerInput
from airgun.widgets import EditableEntry
from airgun.widgets import RadioGroup
from airgun.widgets import SatSelect
from airgun.widgets import SatTable

ACTIONS_COLUMN = 4


class CVFRuleActions(View):
    """'Actions' column for content view filter rules. Can contain either
    'Edit' button or 'Save' and 'Cancel'.
    """

    edit = Text(".//button[contains(@ng-click, 'rule.editMode')]")
    save = Text(".//button[contains(@ng-click, 'handleSave()')]")
    cancel = Text(".//button[contains(@ng-click, 'handleCancel()')]")


class CVFRuleVersion(View):
    """'Version' column for content view filter rule. Depending on type (e.g.
    'Equal To', 'Greater Than' etc) can have different set of inputs.
    """

    rule_type = SatSelect(locator=".//select[@ng-model='rule.type']")
    rule = ConditionalSwitchableView(reference='rule_type')
    version_text = Text(".//span[@ng-hide='rule.editMode']//descendant::span[last()]")

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
        """Custom fill to support passing values for all inputs in single tuple
        without the need to specify specific input name.

        :param tuple values: tuple containing values for specific version type
            and its inputs, e.g. `('Equal To', '0.5')` or
            `('Range', '4.1', '4.6')`
        """
        if not isinstance(values, tuple):
            values = (values,)
        was_change = self.rule_type.fill(values[0])
        if len(values) == 1:
            return was_change
        widgets_list = [f'rule.{name}' for name in self.rule.widget_names]
        values = dict(zip(widgets_list, values[1:]))
        return super().fill(values) or was_change

    def read(self):
        """Custom `read` to return "summary" text value, not the dict with
        every included widget separately.
        """
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
            locator
            or ".//span[contains(@class, 'info-label')][normalize-space(.)='{}']"
            "/following-sibling::span[contains(@class, 'info-value')]".format(name)
        )
        super(EditableEntry, self).__init__(parent, locator, logger)


class AffectedRepositoriesTab(SatSecondaryTab):
    """Affected repositories tab contains repositories count inside tab title,
    making it impossible to rely on exact string value. Using ``starts-with``
    instead.
    """

    TAB_NAME = 'Affected Repositories'
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
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
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
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
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
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
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
                locator=".//input[@type='checkbox']" "[@ng-model='filter.original_packages']"
            )
            add_rule = Text(".//button[@ng-click='addRule()']")
            remove_rule = Text(".//button[@ng-click='removeRules(filter)']")
            table = Table(
                locator='//table',
                column_widgets={
                    0: Checkbox(locator=".//input[@type='checkbox']"),
                    'RPM Name': TextInput(locator='.//input'),
                    'Architecture': TextInput(locator='.//input'),
                    'Version': CVFRuleVersion(),
                    ACTIONS_COLUMN: CVFRuleActions(),
                },
            )

    @content_tabs.register(lambda filter_type: filter_type.endswith('Errata'))
    class errata_filter(AddRemoveResourcesView):
        """Combines both 'Errata by ID' and 'Errata by date and type' filters
        as they can't be easily distinguished on UI. For 'Errata by ID' filter
        'Add' and 'List/Remove' tabs are available, for 'Errata by date and
        type' - only 'Erratum Date Range' tab is displayed.
        """

        @View.nested
        class add_tab(AddTab):
            security = Checkbox(locator=".//input[@ng-model='types.security']")
            enhancement = Checkbox(locator=".//input[@ng-model='types.enhancement']")
            bugfix = Checkbox(locator=".//input[@ng-model='types.bugfix']")
            date_type = RadioGroup(".//div[label[contains(@class, 'radio-inline')]]")
            start_date = DatePickerInput(locator=".//input[@ng-model='rule.start_date']")
            end_date = DatePickerInput(locator=".//input[@ng-model='rule.end_date']")
            select_all = Checkbox(locator=".//table//th[@class='row-select']/input")

            def search(self, query=None, filters=None):
                """Custom search which supports all errata filters.

                :param str optional query: search query to type into search
                    box. Optional as sometimes filtering is enough to find
                    desired errata
                :param dict optional filters: dictionary containing widget
                    names and values to set (like with regular `fill()`)
                """
                if isinstance(filters, dict):
                    for key, value in filters.items():
                        getattr(self, key).fill(value)
                if query:
                    self.searchbox.search(query)
                return self.table.read()

            def add(self, errata_id=None, filters=None):
                """Add specific errata to filter or all available if id not
                provided.

                :param str optional errata_id: ID of errata to add. If not
                    provided - all available errata in table will be selected
                    (especially useful together with filtering)
                :param dict optional filters: dictionary containing widget
                    names and values to set (like with regular `fill()`)
                """
                query = None
                if errata_id:
                    query = f'errata_id = {errata_id}'
                self.search(query, filters)
                if errata_id:
                    self.table.row(('Errata ID', errata_id))[0].widget.fill(True)
                else:
                    self.select_all.fill(True)
                self.add_button.click()

            def fill(self, errata_id=None, filters=None):
                self.add(errata_id, filters)

        @View.nested
        class erratum_date_range(SatSecondaryTab):
            TAB_NAME = 'Erratum Date Range'

            security = Checkbox(locator=".//input[@ng-model='types.security']")
            enhancement = Checkbox(locator=".//input[@ng-model='types.enhancement']")
            bugfix = Checkbox(locator=".//input[@ng-model='types.bugfix']")
            date_type = RadioGroup(".//div[label[contains(@class, 'radio-inline')]]")
            start_date = DatePickerInput(locator=".//input[@ng-model='rule.start_date']")
            end_date = DatePickerInput(locator=".//input[@ng-model='rule.end_date']")

            save = Text('//button[contains(@ng-click, "handleSave()")]')
            cancel = Text('//button[contains(@ng-click, "handleCancel()")]')

            def after_fill(self, was_change):
                self.save.click()

        def add(self, errata_id=None, filters=None):
            """Add specific errata to filter or all available if id not
                provided.

            :param str optional errata_id: ID of errata to add. If not
                provided - all available errata in table will be selected
                (especially useful together with filtering)
            :param dict optional filters: dictionary containing widget names
                and values to set (like with regular `fill()`)
            """
            return self.add_tab.fill(errata_id, filters)

        def read(self):
            """Read values from tabs depending on errata filter type (by id or
            daterange filter).
            """
            if self.erratum_date_range.is_displayed:
                return {'erratum_date_range': self.erratum_date_range.read()}
            return {
                'assigned': self.list_remove_tab.read(),
                'unassigned': self.add_tab.read(),
            }

    @content_tabs.register(lambda filter_type: filter_type.endswith('Package Groups'))
    class package_group_filter(AddRemoveResourcesView):
        pass

    @content_tabs.register(lambda filter_type: filter_type.endswith('Module Streams'))
    class module_streams_filter(AddRemoveResourcesView):
        pass

    @View.nested
    class affected_repositories(AffectedRepositoriesTab):
        filter_toggle = RadioGroup(".//div[@class='col-sm-8']")
        product_filter = Select(locator=".//select[@ng-model='product']")
        searchbox = TextInput(locator=".//input[@ng-model='repositorySearch']")
        update_repositories = Button('Update Repositories')
        select_all = Checkbox(locator=".//table//th[@class='row-select']/input")
        table = SatTable(
            locator='.//table',
            column_widgets={0: Checkbox(locator=".//input[@type='checkbox']")},
        )
