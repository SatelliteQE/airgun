from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.rhai import AllRulesView


class RuleEntity(BaseEntity):

    def search(self, rule_name):
        """Perform the search of a rule."""
        view = self.navigate_to(self, "All")
        view.search.fill(rule_name)


@navigator.register(RuleEntity, "All")
class RulesDetails(NavigateStep):
    """Navigate to Red Hat Access Insights Rules screen."""
    VIEW = AllRulesView

    def step(self, *args, **kwargs):
        self.view.menu.select("Insights", "Rules")
