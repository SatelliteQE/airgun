from wait_for import wait_for
from widgetastic.widget import Checkbox
from widgetastic.widget import ConditionalSwitchableView
from widgetastic.widget import Select
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView
from airgun.widgets import RadioGroup


class SyncTemplatesView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    title = Text("//h2[contains(., 'Import or Export Templates')]")
    sync_type = RadioGroup("//div[label[contains(., 'Action type')]]")
    submit = Text("//button[@type='submit']")

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
        associate = Select(name='associate')
        branch = TextInput(name='branch')
        dirname = TextInput(name='dirname')
        filter = TextInput(name='filter')
        force_import = Checkbox(name='force')
        lock = Checkbox(name='lock')
        negate = Checkbox(name='negate')
        prefix = TextInput(name='prefix')
        repo = TextInput(name='repo')

    @template.register('Export')
    class ExportTemplates(View):
        branch = TextInput(name='branch')
        dirname = TextInput(name='dirname')
        filter = TextInput(name='filter')
        metadata_export_mode = Select(name='metadata_export_mode')
        negate = Checkbox(name='negate')
        repo = TextInput(name='repo')


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
