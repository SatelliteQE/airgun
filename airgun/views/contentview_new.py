from wait_for import wait_for
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import Checkbox, ParametrizedView, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb, Tab
from widgetastic_patternfly4 import Button, Dropdown, Modal, Radio as PF4Radio, Select
from widgetastic_patternfly4.ouia import (
    Button as PF4Button,
    ExpandableTable,
    PatternflyTable,
    Select as PF4Select,
    Switch,
)

from airgun.views.common import (
    BaseLoggedInView,
    NewAddRemoveResourcesView,
    PF4LCECheckSelectorGroup,
    PF4LCESelectorGroup,
    SearchableViewMixinPF4,
)
from airgun.widgets import (
    ActionsDropdown,
    ConfirmationDialog,
    EditableEntry,
    PF4ProgressBar,
    PF4Search,
    ReadOnlyEntry,
)

LOCATION_NUM = 3


class ContentViewAddResourcesView(NewAddRemoveResourcesView):
    remove_button = Dropdown(locator='.//div[@data-ouia-component-id="cv-components-bulk-actions"]')
    add_button = Button(locator='.//button[@data-ouia-component-id="add-content-views"]')
    table = PatternflyTable(
        component_id='content-view-components-table',
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            'Type': Text('.//a'),
            'Name': Text('.//a'),
            'Version': Text('.//a'),
            'Environments': Text('.//td[5]'),
            'Repositories': Text('.//a'),
            'Status': Text('.//a'),
            'Description': Text('.//a'),
            8: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
        },
    )

    @property
    def is_displayed(self):
        return self.table.is_displayed


class AddContentViewModal(BaseLoggedInView):
    title = Text('.//div[@data-ouia-component-id="add-content-views"]')
    submit_button = PF4Button('add-components-modal-add')
    cancel_button = PF4Button('add-components-modal-cancel')

    version_select = Select(locator=".//div[@data-ouia-component-id='add-content-views']")
    always_update = Checkbox(locator=".//input[@class='pf-c-check__input']")

    @property
    def is_displayed(self):
        return self.title.is_displayed


class ContentViewTableView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text('.//h1[@data-ouia-component-id="cvPageHeaderText"]')
    create_content_view = PF4Button('create-content-view')
    table = ExpandableTable(
        component_id='content-views-table',
        column_widgets={
            'Type': Text('./a'),
            'Name': Text('./a'),
            'Last Published': ('./a'),
            'Last task': Text('.//a'),
            'Latest version': Text('.//a'),
            6: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
        },
    )

    @property
    def is_displayed(self):
        return self.create_content_view.is_displayed


class ContentViewCreateView(BaseLoggedInView):
    title = Text('.//div[@data-ouia-component-id="create-content-view-modal"]')
    name = TextInput(id='name')
    label = TextInput(id='label')
    description = TextInput(id='description')
    submit = PF4Button('create-content-view-form-submit')
    cancel = PF4Button('create-content-view-form-cancel')

    component_tile = Text('//div[contains(@id, "component")]')
    solve_dependencies = Checkbox(id='dependencies')
    import_only = Checkbox(id='importOnly')
    composite_tile = Text('//div[contains(@id, "composite")]')
    auto_publish = Checkbox(id='autoPublish')

    @property
    def is_displayed(self):
        return self.title.is_displayed

    def after_fill(self, value):
        """Ensure 'Create content view' button is enabled after filling out the required fields"""
        self.submit.wait_displayed()


class ContentViewEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb('breadcrumbs-list')
    search = PF4Search()
    dialog = ConfirmationDialog()
    publish = PF4Button('cv-details-publish-button')
    # click the cv_actions dropdown, then click copy or delete
    cv_actions = ActionsDropdown('//div[@data-ouia-component-id="cv-details-actions"]')
    cv_copy = Text('//a[@data-ouia-component-id="cv-copy"]')
    cv_delete = Text('//a[@data-ouia-component-id="cv-delete"]')

    # buttons for wizard: deleting a CV with Version promoted to environment(s)
    next_button = Button('Next')
    delete_finish = Button('Delete')
    back_button = Button('Back')
    cancel_button = Button('Cancel')
    close_button = Button('Close')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return breadcrumb_loaded and self.breadcrumb.locations[0] == 'Content Views'

    @View.nested
    class details(Tab):
        TAB_LOCATOR = ParametrizedLocator('//a[contains(@href, "#/details")]')
        name = EditableEntry(name='Name')
        label = ReadOnlyEntry(name='Label')
        type = ReadOnlyEntry(name='Composite?')
        description = EditableEntry(name='Description')
        # depSolv is maybe a conditionalswitch
        solve_dependencies = Switch(name='solve_dependencies switch')
        import_only = Switch(name='import_only_switch')

    @View.nested
    class versions(Tab):
        TAB_LOCATOR = ParametrizedLocator(
            '//a[contains(@href, "#/versions") and @data-ouia-component-id="routed-tabs-tab-versions"]'
        )
        searchbox = PF4Search()
        table = PatternflyTable(
            component_id="content-view-versions-table",
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                'Version': Text('.//a'),
                'Environments': Text('.//td[3]'),
                'Packages': Text('.//a'),
                'Errata': Text('.//a'),
                'Additional content': Text('.//a'),
                'Description': Text('.//a'),
                7: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
            },
        )
        publishButton = PF4Button('cv-details-publish-button')

        def search(self, version_name):
            """Searches for content view version.
            Searchbox can't search by version name, only by number, that's why in
            case version name was passed, it's transformed into recognizable
            value before filling, for example - Version 1.0' -> 'version = 1'
            """
            search_phrase = version_name
            if version_name.startswith('V') and '.' in version_name:
                search_phrase = f'version = {version_name.split()[1].split(".")[0]}'
            self.searchbox.search(search_phrase)
            return self.table.read()

    @View.nested
    class content_views(Tab):
        TAB_LOCATOR = ParametrizedLocator('//a[contains(@href, "#/contentviews")]')

        resources = View.nested(ContentViewAddResourcesView)

    @View.nested
    class repositories(Tab):
        TAB_LOCATOR = ParametrizedLocator('//a[contains(@href, "#/repositories")]')
        resources = View.nested(NewAddRemoveResourcesView)

    @View.nested
    class filters(Tab):
        TAB_LOCATOR = ParametrizedLocator('//a[contains(@href, "#/filters")]')
        new_filter = PF4Button('create-filter-button')
        searchbox = PF4Search()
        table = PatternflyTable(
            component_id="content-view-filters-table",
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                'Name': Text('.//a'),
                'Description': Text('.//a'),
                'Updated': Text('.//a'),
                'Content type': Text('.//a'),
                'Inclusion type': Text('.//a'),
                6: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
            },
        )

        def search(self, name):
            """Searches for specific filter'"""
            self.searchbox.search(name)
            return self.table.read()


class ContentViewVersionPublishView(BaseLoggedInView):
    # publishing view is a popup so adding all navigation within the same context
    ROOT = './/div[contains(@class,"pf-c-wizard")]'
    title = Text(".//h2[contains(., 'Publish') and contains(@aria-label, 'Publish')]")
    publish_alert = Text(".//h4[contains(., 'No available repository or filter updates')]")
    # publishing screen
    description = TextInput(id='description')
    promote = Switch('promote-switch')

    next_button = Button('Next')
    finish_button = Button('Finish')
    back_button = Button('Back')
    cancel_button = Button('Cancel')
    close_button = Button('Close')
    progressbar = PF4ProgressBar('.//div[contains(@class, "pf-c-wizard__main-body")]')
    lce_selector = ParametrizedView.nested(PF4LCECheckSelectorGroup)

    @property
    def is_displayed(self):
        return self.title.is_displayed

    def wait_animation_end(self):
        wait_for(
            lambda: 'in' in self.browser.classes(self),
            handle_exception=True,
            logger=self.logger,
            timeout=10,
        )

    def before_fill(self, values=None):
        """If we don't want to break view.fill() procedure flow, we need to
        push 'Edit' button to open necessary dialog to be able to fill values
        """
        self.promote.click()
        wait_for(
            lambda: self.lce.is_displayed is True,
            timeout=30,
            delay=1,
            logger=self.logger,
        )


class ContentViewVersionPromoteView(Modal):
    ROOT = './/div[@data-ouia-component-id="promote-version"]'

    description = Text('.//h2[@data-ouia-component-id="description-text-value"]')
    lce_selector = ParametrizedView.nested(PF4LCESelectorGroup)
    promote_btn = Button(locator='//button[normalize-space(.)="Promote"]')
    cancel_btn = Button(locator='//button[normalize-space(.)="Cancel"]')


class ContentViewVersionDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    version = Text(locator='.//h2[@data-ouia-component-id="cv-version"]')
    version_dropdown = Dropdown(
        locator='.//div[@data-ouia-component-id="cv-version-header-actions-dropdown"]'
    )
    promoteButton = PF4Button(
        locator='.//button[@data-ouia-component-id="cv-details-publish-button"]'
    )
    editDescription = PF4Button(
        locator='.//button[@data-ouia-component-id="edit-button-description"]'
    )
    # buttons for wizard: deleting a version promoted to environment(s)
    next_button = Button('Next')
    delete_finish = Button('Delete')
    back_button = Button('Back')
    cancel_button = Button('Cancel')
    close_button = Button('Close')
    progressbar = PF4ProgressBar('.//div[contains(@class, "pf-c-wizard__main-body")]')

    @View.nested
    class repositories(Tab):
        TAB_LOCATOR = ParametrizedLocator(
            './/button[@data-ouia-component-id="cv-version-details-tabs-tab-repositories"]'
        )
        searchbox = PF4Search()
        table = PatternflyTable(
            component_id="content-view-version-details-repositories-table",
            column_widgets={
                'Name': Text('.//a'),
                'Version': Text('.//a'),
                'Release': Text('.//a'),
                'Arch': Text('.//a'),
                'Epoch': Text('.//a'),
            },
        )

    @View.nested
    class rpmPackages(Tab):
        TAB_LOCATOR = ParametrizedLocator(
            './/button[@data-ouia-component-id="cv-version-details-tabs-tab-rpmPackages"]'
        )
        searchbox = PF4Search()
        table = PatternflyTable(
            component_id='content-view-version-details-rpm-packages-table',
            column_widgets={
                'Name': Text('.//a'),
                'Type': Text('.//a'),
                'Product': Text('.//a'),
                'Content': Text('.//a'),
            },
        )

    @View.nested
    class rpmPackageGroups(Tab):
        TAB_LOCATOR = ParametrizedLocator(
            './/button[@data-ouia-component-id="cv-version-details-tabs-tab-rpmPackageGroups"]'
        )
        searchbox = PF4Search()
        table = PatternflyTable(
            component_id='content-view-version-details-rpm-package-groups-table',
            column_widgets={
                'Name': Text('.//a'),
                'Repository': Text('.//a'),
            },
        )

    @View.nested
    class errata(Tab):
        TAB_LOCATOR = ParametrizedLocator(
            './/button[@data-ouia-component-id="cv-version-details-tabs-tab-errata"]'
        )
        searchbox = PF4Search()
        table = PatternflyTable(
            component_id='content-view-version-details-errata-table',
            column_widgets={
                'Errata ID': Text('.//a'),
                'Title': Text('.//a'),
                'Type': Text('.//a'),
                'Modular': Text('.//a'),
                'Applicable Content Hosts': Text('.//a'),
                'Updated': Text('.//a'),
            },
        )

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and len(self.breadcrumb.locations) > LOCATION_NUM
            and self.breadcrumb.locations[0] == 'Content views'
            and self.breadcrumb.locations[2] == 'Versions'
        )


class CreateFilterView(View):
    ROOT = './/div[@data-ouia-component-id="create-filter-modal"]'

    name = TextInput(id='name')
    filterType = PF4Select('content_type')
    includeFilter = PF4Radio(label_text='Include filter')
    excludeFilter = PF4Radio(label_test='Exclude filter')
    create = PF4Button('create-filter-form-submit-button')
    cancel = PF4Button('create-filter-form-cancel-button')


class EditFilterView(View):
    name = Text('.//h2[@data-ouia-component-id="name-text-value"]')
    editName = PF4Button('edit-button-name')
    nameInput = TextInput('name text input')
    submitName = PF4Button('submit-button-name')
    clearName = PF4Button('clear-button-name')
    description = Text('.//h2[@data-ouia-component-id="description-text-value"]')
    editDescription = PF4Button('edit-button-description')
    descriptionInput = TextInput(locator='.//textarea[@aria-label="description text area"]')

    # Below this, the fields are generally not shared by each Filter Type

    # RPM Rule
    search = PF4Search()
    addRpmRule = PF4Button('add-rpm-rule-button')
    rpmRuleTable = PatternflyTable(
        component_id="content-view-rpm-filter-table",
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            'RPM Name': Text('.//a'),
            'Architecture': Text('.//a'),
            'Versions': Text('.//a'),
            4: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
        },
    )

    # Container Image Tag Rule
    addTagRule = PF4Button('add-content-view-container-image-filter-button')
    tagRuleTable = PatternflyTable(
        component_id="content-view-container-image-filter",
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            'Tag Name': Text('.//a'),
            2: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
        },
    )

    # Package Group Rule
    addPackageGroupRule = PF4Button('add-package-group-filter-rule-button')
    removePackageGroupRule = Dropdown('cv-package-group-filter-bulk-actions-dropdown')
    packageGroupRuleTable = PatternflyTable(
        component_id="content-view-package-group-filter-table",
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            'Name': Text('.//a'),
            'Product': Text('.//a'),
            'Repository': Text('.//a'),
            'Description': Text('.//a'),
            'Status': Text('.//a'),
            6: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
        },
    )

    # Module Streams Rule
    addModuleStreamRule = PF4Button('add-module-stream-rule-button')
    removeModuleStreamRule = Dropdown('bulk-actions-dropdown')
    moduleStreamRuleTable = PatternflyTable(
        component_id="content-view-module-stream-filter-table",
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            'Name': Text('.//a'),
            'Stream': Text('.//a'),
            'Version': Text('.//a'),
            'Context': Text('.//a'),
            'Status': Text('.//a'),
            6: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
        },
    )

    # Errata Rule
    addErrataRule = PF4Button('add-errata-id-button')
    removeErratRule = Dropdown('cv-errata-id-bulk-action-dropdown')
    moduleErrataTable = PatternflyTable(
        component_id="content-view-errata-by-id-filter-table",
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            'Errata ID': Text('.//a'),
            'Type': Text('.//a'),
            'Issued': Text('.//a'),
            'Updated': Text('.//a'),
            'Severity': Text('.//a'),
            'Synopsis': Text('.//a'),
            'Status': Text('.//a'),
            8: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
        },
    )

    # Errata by Date Range

    saveErrataByDate = PF4Button('save-filter-rule-button')
    cancelErrataByDate = PF4Button('cancel-save-filter-rule-button')

    @property
    def is_displayed(self):
        return self.name.is_displayed


class AddRPMRuleView(View):
    ROOT = './/div[@data-ouia-component-id="add-edit-rpm-rule-modal"]'

    rpmName = TextInput(
        locator=".//div[contains(.//span, 'RPM name') and @class='pf-c-form__group']/*//input"
    )
    architecture = TextInput(
        locator=".//div[contains(.//span, 'Architecture') and @class='pf-c-form__group']/*//input"
    )

    versions = PF4Select('version-comparator')
    addEdit = PF4Button('add-edit-package-modal-submit')
    cancel = PF4Button('add-edit-package-modal-cancel')


class AddContainerTagRuleView(View):
    ROOT = './/div[@data-ouia-component-id="add-edit-container-tag-rule-modal"]'

    tagName = TextInput(
        locator=".//div[contains(.//span, 'Tag name') and @class='pf-c-form__group']/*//input"
    )

    addEdit = PF4Button('add-edit-container-tag-filter-rule-submit')
    cancel = PF4Button('add-edit-container-tag-filter-rule-cancel')
