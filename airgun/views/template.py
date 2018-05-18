from widgetastic.widget import Checkbox, Text, TextInput, View

from airgun.views.common import (
    BaseLoggedInView,
    SatTab,
    SatTable,
    SearchableViewMixin,
    TemplateEditor,
)
from airgun.widgets import ActionsDropdown, FilteredDropdown, MultiSelect


class ProvisioningTemplatesView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[contains(., 'Provisioning Templates')]")
    new = Text("//a[contains(@href, '/templates/provisioning_templates/new')]")
    table = SatTable(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class ProvisioningTemplateDetailsView(BaseLoggedInView):
    FORM = "//form[contains(@id, 'provisioning_template')]"
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.FORM, exception=False) is not None

    @View.nested
    class template(SatTab):
        name = TextInput(id='provisioning_template_name')
        default = Checkbox(id='provisioning_template_default')
        template_editor = View.nested(TemplateEditor)
        audit = TextInput(id='provisioning_template_audit_comment')

    @View.nested
    class type(SatTab):
        snippet = Checkbox(id='provisioning_template_snippet')
        template_type = FilteredDropdown(
            id='provisioning_template_template_kind')

    @View.nested
    class association(SatTab):
        applicable_os = MultiSelect(
            id='ms-provisioning_template_operatingsystem_ids')

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(
            id='ms-provisioning_template_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(
            id='ms-provisioning_template_organization_ids')
