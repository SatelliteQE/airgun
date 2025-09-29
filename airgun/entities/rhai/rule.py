from airgun.entities.base import BaseEntity
from airgun.entities.rhai.base import InsightsNavigateStep
from airgun.navigation import navigator
from airgun.views.rhai import AllRulesView


class RuleEntity(BaseEntity):
    endpoint_path = "/redhat_access/insights/rules"

    def search(self, rule_name):
        """Perform the search of a rule."""
        view = self.navigate_to(self, "All")
        view.search.fill(rule_name)


@navigator.register(RuleEntity, "All")
class RulesDetails(InsightsNavigateStep):
    """Navigate to Red Hat Access Insights Rules screen."""

    VIEW = AllRulesView

    def step(self, *args, **kwargs):
        self.view.menu.select("Insights", "Rules")
