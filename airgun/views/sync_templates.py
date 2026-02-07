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
from widgetastic_patternfly5 import PatternflyTable as PF5Table

from airgun.views.common import BaseLoggedInView
from airgun.widgets import PF5RadioGroup


class SyncTemplatesView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    title = Text("//h1[contains(., 'Import or Export Templates')]")
    sync_type = PF5RadioGroup("//div[@id='sync-type_formGroup']")
    submit = Text(".//button[contains(.,'Submit')]")

    template = ConditionalSwitchableView(reference='sync_type')

    @property
    def is_displayed(self):
        return self.breadcrumb.is_displayed and self.title.is_displayed

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
        lock = Select(name='lock')
        negate = Checkbox(name='negate')
        prefix = TextInput(name='prefix')
        repo = TextInput(name='repo')
        http_proxy_policy = Select(name='http_proxy_policy')
        http_proxy_id = Select(name='http_proxy_id')

        def fill(self, items):
            if 'http_proxy_id' in items:
                self.http_proxy_policy.fill(items['http_proxy_policy'])
            super().fill(items)

    @template.register('Export')
    class ExportTemplates(View):
        branch = TextInput(name='branch')
        dirname = TextInput(name='dirname')
        filter = TextInput(name='filter')
        metadata_export_mode = Select(name='metadata_export_mode')
        negate = Checkbox(name='negate')
        repo = TextInput(name='repo')
        http_proxy_policy = Select(name='http_proxy_policy')
        http_proxy_id = Select(name='http_proxy_id')


class TemplatesReportView(BaseLoggedInView):
    title = Text('//h1')
    REPORTS = PF5Table(locator='.//table[contains(@data-ouia-component-id, "foreman-templates")]')

    @property
    def is_displayed(self):
        return all(
            [
                self.title.is_displayed,
                self.browser.elements(self.REPORTS),
            ]
        )
