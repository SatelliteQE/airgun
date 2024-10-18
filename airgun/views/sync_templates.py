from wait_for import wait_for
from widgetastic.widget import (
    Checkbox,
    ConditionalSwitchableView,
    Select,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView
from airgun.widgets import RadioGroup


class SyncTemplatesView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    title = Text("//h2[contains(., 'Import or Export Templates')]")
    sync_type = RadioGroup("//div[label[contains(., 'Action type')]]")
    submit = Text(".//button[contains(.,'Submit')]")

    template = ConditionalSwitchableView(reference='sync_type')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.browser.wait_for_element(self.title, exception=False) is not None
        )

    def before_fill(self, values):
        """Wait for Sync Type Radio Button to be displayed"""
        wait_for(lambda: self.sync_type.is_displayed, timeout=10, delay=1, logger=self.logger)

    @template.register('Import')
    class ImportTemplates(View):
        associate = Select(name='import.associate')
        branch = TextInput(name='import.branch')
        dirname = TextInput(name='import.dirname')
        filter = TextInput(name='import.filter')
        force_import = Checkbox(name='import.force')
        lock = Select(name='import.lock')
        negate = Checkbox(name='import.negate')
        prefix = TextInput(name='import.prefix')
        repo = TextInput(name='import.repo')

    @template.register('Export')
    class ExportTemplates(View):
        branch = TextInput(name='export.branch')
        dirname = TextInput(name='export.dirname')
        filter = TextInput(name='export.filter')
        metadata_export_mode = Select(name='export.metadata_export_mode')
        negate = Checkbox(name='export.negate')
        repo = TextInput(name='export.repo')


class TemplatesReportView(BaseLoggedInView):
    title = Text("//h1")
    REPORTS = "//div[contains(@class, 'list-group-item')]"

    @property
    def is_displayed(self):
        return all(
            [
                self.browser.wait_for_element(self.title, exception=False),
                self.browser.elements(self.REPORTS),
            ]
        )
