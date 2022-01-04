from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.utils import retry_navigation
from airgun.views.sync_templates import SyncTemplatesView
from airgun.views.sync_templates import TemplatesReportView


class SyncTemplatesEntity(BaseEntity):
    endpoint_path = '/template_syncs'

    def sync(self, values):
        """Import Export Switch Action Entity"""
        view = self.navigate_to(self, 'Sync')
        view.fill(values)
        view.submit.click()
        self.browser.plugin.ensure_page_safe()
        if view.validations.messages:
            raise AssertionError(
                f'Validation Errors are present on Page. Messages are {view.validations.messages}'
            )
        reports_view = TemplatesReportView(self.browser)
        wait_for(
            lambda: reports_view.is_displayed is True,
            timeout=60,
            delay=1,
            logger=reports_view.logger,
        )
        return reports_view.title.read()


@navigator.register(SyncTemplatesEntity, 'Main')
class SyncMainPageNavigation(NavigateStep):
    """Navigate to Import/Export Templates page"""

    VIEW = SyncTemplatesView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Sync Templates')


@navigator.register(SyncTemplatesEntity, 'Sync')
class SyncTemplatesActionNavigation(NavigateStep):
    """Navigate to Import/Export Templates page"""

    VIEW = SyncTemplatesView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'Main')
