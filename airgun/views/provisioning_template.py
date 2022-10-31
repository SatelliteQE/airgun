from widgetastic.widget import Checkbox
from widgetastic.widget import Select
from widgetastic.widget import Table
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly import Button

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SatTab
from airgun.views.common import SearchableViewMixin
from airgun.views.common import TemplateEditor
from airgun.views.common import TemplateInputItem
from airgun.widgets import ActionsDropdown
from airgun.widgets import FilteredDropdown
from airgun.widgets import GenericRemovableWidgetItem
from airgun.widgets import MultiSelect
from airgun.widgets import RemovableWidgetsItemsListView


class TemplateHostEnvironmentAssociation(GenericRemovableWidgetItem):
    """Provisioning Template Foreign Input Set Item widget"""

    remove_button = Text(".//a[@title='Remove Combination']")
    host_group = Select(locator=".//select[contains(@name, '[hostgroup_id]')]")


class ProvisioningTemplatesView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[normalize-space(.)='Provisioning Templates']")
    new = Button("Create Template")
    build_pxe_default = Button("Build PXE Default")
    table = Table(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Locked': Text('.'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ProvisioningTemplateDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Provisioning Templates'
            and self.breadcrumb.read().startswith('Edit ')
        )

    @View.nested
    class template(SatTab):
        name = TextInput(id='provisioning_template_name')
        default = Checkbox(id='provisioning_template_default')
        template_editor = View.nested(TemplateEditor)
        audit = TextInput(id='provisioning_template_audit_comment')

    @View.nested
    class inputs(RemovableWidgetsItemsListView, SatTab):
        ITEMS = ".//div[contains(@class, 'template_inputs')]/following-sibling::div"
        ITEM_WIDGET_CLASS = TemplateInputItem
        add_item_button = Text(".//a[@data-association='template_inputs']")

    @View.nested
    class type(SatTab):
        snippet = Checkbox(id='provisioning_template_snippet')
        template_type = FilteredDropdown(id='provisioning_template_template_kind')

    @View.nested
    class association(SatTab):
        applicable_os = MultiSelect(id='ms-provisioning_template_operatingsystem_ids')

        @View.nested
        class valid_hostgroups(RemovableWidgetsItemsListView):
            ROOT = "//div[@id='association']"
            ITEMS = ".//fieldset[@id='template_combination']/div"
            ITEM_WIDGET_CLASS = TemplateHostEnvironmentAssociation
            add_item_button = Text(".//a[normalize-space(.)='+ Add Combination']")

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(id='ms-provisioning_template_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(id='ms-provisioning_template_organization_ids')


class ProvisioningTemplateCreateView(ProvisioningTemplateDetailsView):
    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Provisioning Templates'
            and self.breadcrumb.read() == 'Create Template'
        )
