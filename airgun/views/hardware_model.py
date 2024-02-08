from widgetastic.widget import Text, TextInput
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly4 import Dropdown

from airgun.views.common import BaseLoggedInView, SearchableViewMixinPF4
from airgun.widgets import Pf4ConfirmationDialog, SatTable


class DeleteHardwareModelDialog(Pf4ConfirmationDialog):
    confirm_dialog = Text(".//button[contains(normalize-space(.),'Delete')]")
    cancel_dialog = Text(".//button[normalize-space(.)='Cancel']")


class HardwareModelsView(BaseLoggedInView, SearchableViewMixinPF4):
    delete_dialog = DeleteHardwareModelDialog()
    title = Text("//h1[normalize-space(.)='Hardware models']")
    new = Text("//a[contains(@href, '/models/new')]")
    table = SatTable(
        './/table',
        column_widgets={
            'Name': Text('.//a'),
            4: Dropdown(),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class HardwareModelCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='model_name')
    hardware_model = TextInput(id='model_hardware_model')
    vendor_class = TextInput(id='model_vendor_class')
    info = TextInput(id='model_info')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Hardware Models'
            and self.breadcrumb.read() == 'Create Model'
        )


class HardwareModelEditView(HardwareModelCreateView):
    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Hardware Models'
            and self.breadcrumb.read().startswith('Edit ')
        )
