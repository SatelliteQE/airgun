from widgetastic.widget import Checkbox, Text, TextInput, View
from airgun.views.template import (
    TemplatesView,
    TemplateDetailsView,
    TemplateCreateView,
)
from airgun.views.common import (
    SatTab,
    SearchableViewMixin,
    TemplateEditor,
)
from airgun.widgets import (
    FilteredDropdown,
    MultiSelect,
)


class ProvisioningTemplatesView(TemplatesView):
    title = Text("//h1[contains(., 'Provisioning Templates')]")
    new = Text("//a[contains(@href, '/templates/provisioning_templates/new')]")


class ProvisioningTemplateDetailsView(TemplateDetailsView):
    FORM = "//form[contains(@id, 'provisioning_template')]"

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Provisioning templates'
                and self.breadcrumb.read().startswith('Edit ')
        )

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


class ProvisioningTemplateCreateView(TemplateCreateView, ProvisioningTemplateDetailsView):

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Provisioning templates'
            and self.breadcrumb.read() == 'Create Template'
        )
