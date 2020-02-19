from navmazing import NavigateToSibling
from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.entities.rhai.base import InsightsNavigateStep
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.rhai import AddPlanView
from airgun.views.rhai import AllPlansView
from airgun.views.rhai import PlanEditView
from airgun.views.rhai import PlanModalWindow


class PlanEntity(BaseEntity):
    endpoint_path = '/redhat_access/insights/planner'

    def create(self, name, rules):
        """Create a new RHAI Plan entity."""
        view = self.navigate_to(self, "Add")
        view.name.fill(name)
        for rule in rules:
            view.rules_filter.fill(rule)
            view.actions[0][0].widget.fill(True)
        view.save.click()

    def delete(self, entity_name):
        """Delete RHAI Plan entity."""
        view = self.navigate_to(
            self, "Details", entity_name=entity_name).plan(entity_name)
        wait_for(lambda: view.delete.is_displayed)
        view.delete.click()
        modal = PlanModalWindow(self.session.browser)
        modal.yes.click()

    def update(self, entity_name, values):
        """Update RHAI Plan entity."""
        view = self.navigate_to(
            self, "Details", entity_name=entity_name).plan(entity_name)
        view.edit.click()
        view = PlanEditView(self.session.browser)
        view.fill_with(values, on_change=view.save.click)


@navigator.register(PlanEntity, "All")
class AllPlans(InsightsNavigateStep):
    """Navigate to Insights Planner screen."""
    VIEW = AllPlansView

    def step(self, *args, **kwargs):
        self.view.menu.select("Insights", "Planner")


@navigator.register(PlanEntity, "Add")
class AddPlan(NavigateStep):
    """Navigate to Insights Plan builder screen."""
    VIEW = AddPlanView
    prerequisite = NavigateToSibling("All")

    def step(self, *args, **kwargs):
        self.parent.create_plan.click()


@navigator.register(PlanEntity, "Details")
class PlanDetails(NavigateStep):
    """Navigate to Insights plan details screen.

    Args:
        entity_name: plan name
    """
    VIEW = AllPlansView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, "All")

    def step(self, *args, **kwargs):
        self.view.plan(kwargs["entity_name"]).title.click()
