from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.audit import AuditsView


class AuditEntity(BaseEntity):
    endpoint_path = '/audits'

    def search(self, value):
        """Search for audit entry in logs and return first one from the list"""
        view = self.navigate_to(self, 'All')
        return view.search(value)


@navigator.register(AuditEntity, 'All')
class ShowAllAuditEntries(NavigateStep):
    """Navigate to Audit screen that contains all log entries"""
    VIEW = AuditsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Monitor', 'Audits')
