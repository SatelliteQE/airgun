from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.task import TaskDetailsView, TasksView


class TaskEntity(BaseEntity):

    def search(self, value):
        """Search for specific task"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read_all(self):
        """Read all tasks widgets values from the title page"""
        view = self.navigate_to(self, 'All')
        return view.read()

    def read(self, entity_name, widget_names=None):
        """Read specific task values from details page"""
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        return view.read(widget_names=widget_names)


@navigator.register(TaskEntity, 'All')
class ShowAllTasks(NavigateStep):
    """Navigate to All Tasks page"""
    VIEW = TasksView

    def step(self, *args, **kwargs):
        self.view.menu.select('Monitor', 'Tasks')


@navigator.register(TaskEntity, 'Details')
class TaskDetails(NavigateStep):
    """Navigate to Task Details screen.

         Args:
            entity_name: name of the task
    """
    VIEW = TaskDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(action=entity_name)['Action'].widget.click()
