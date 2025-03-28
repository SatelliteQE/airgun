from widgetastic.widget import (
    Checkbox,
    ConditionalSwitchableView,
    Table,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb, Button

from airgun.views.common import (
    BaseLoggedInView,
    SatTab,
    SearchableViewMixinPF4,
    TemplateInputItem,
)
from airgun.widgets import (
    ACEEditor,
    ActionsDropdown,
    FilteredDropdown,
    MultiSelect,
    RemovableWidgetsItemsListView,
)


class PartitionTablesView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[text()='Partition Tables']")
    new = Button("Create Partition Table")
    table = Table(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class PartitionTableEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @View.nested
    class template(SatTab):
        name = TextInput(id='ptable_name')
        default = Checkbox(id='ptable_default')
        snippet = Checkbox(locator="//input[@id='ptable_snippet']")
        os_family_selection = ConditionalSwitchableView(reference='snippet')

        @os_family_selection.register(True)
        class SnippetOption(View):
            pass

        @os_family_selection.register(False)
        class OSFamilyOption(View):
            os_family = FilteredDropdown(id='ptable_os_family')

        template_editor = ACEEditor()
        audit_comment = TextInput(id='ptable_audit_comment')

    @View.nested
    class inputs(RemovableWidgetsItemsListView, SatTab):
        ITEMS = ".//div[contains(@class, 'template_inputs')]/following-sibling::div"
        ITEM_WIDGET_CLASS = TemplateInputItem
        add_item_button = Text(".//a[@data-association='template_inputs']")

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(id='ms-ptable_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(id='ms-ptable_organization_ids')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Partition Tables'
            and self.breadcrumb.read().startswith('Edit ')
        )


class PartitionTableCreateView(PartitionTableEditView):
    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Partition Tables'
            and self.breadcrumb.read() == 'Create Partition Table'
        )
