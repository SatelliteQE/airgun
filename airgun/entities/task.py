import time

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.task import TaskDetailsView, TasksView


class TaskEntity(BaseEntity):
    endpoint_path = '/foreman_tasks/tasks'

    def search(self, value):
        """Search for specific task"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read_all(self, widget_names=None):
        """Read all tasks widgets values from the title page.
        Or read specific widgets by adding 'widget_names' parameter
        """
        view = self.navigate_to(self, 'All')
        return view.read(widget_names=widget_names)

    def read(self, entity_name, widget_names=None):
        """Read specific task values from details page"""
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        time.sleep(3)
        return view.read(widget_names=widget_names)

    def set_chart_filter(self, chart_name, index=None):
        """Remove filter from searchbox and set filter from specific chart

        :param index: index in 'StoppedChart' table,
            dict with 'row' number and 'focus' as column name
        """
        view = self.navigate_to(self, 'All')
        chart = getattr(view, chart_name)
        view.searchbox.clear()
        if chart_name == 'StoppedChart' and index:
            chart.table[index['row']][index['focus']].click()
        else:
            chart.name.click()

    def total_items(self):
        """Get total items displayed in the table"""
        view = self.navigate_to(self, 'All')
        return view.pagination.total_items


@navigator.register(TaskEntity, 'All')
class ShowAllTasks(NavigateStep):
    """Navigate to All Tasks page"""

    VIEW = TasksView

    @retry_navigation
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
