from navmazing import NavigateToSibling
from widgetastic.exceptions import RowNotFound

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.trend import TrendCreateView
from airgun.views.trend import TrendEditView
from airgun.views.trend import TrendsView


class TrendEntity(BaseEntity):
    endpoint_path = '/trends'

    def create(self, values):
        """Create new trend in the system

        Please note that we have static amount of Trend types and trendables, so it is not
        possible to generate values for them. In case you want to interact with them through
        automation, it is must have condition to provide unique elements from corresponding
        lists. In most cases it will not be possible to re-run tests due condition of
        uniqueness described above.

        :param values: values for new trend entity
        """
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def update(self, entity_name, row_name, value):
        """Update existing trend parameter to a new value

        :param entity_name: name of the trend to be updated
        :param row_name: name of trend parameter to be changed
        :param value: New value of trend parameter
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        next(view.table.rows((0, row_name)))['Display Name'].widget.fill(value)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete existing trend

        :param entity_name: name of the trend to be deleted
        """
        view = self.navigate_to(self, 'All')
        view.table.row(name=entity_name)['Action'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, entity_name):
        """Validate that necessary trend is present in the table

        :param entity_name: name of the trend to be found
        """
        view = self.navigate_to(self, 'All')
        if view.welcome_page.is_displayed:
            return False
        try:
            result = bool(view.table.row(name=entity_name)['Name'].read())
        except RowNotFound:
            result = False
        return result


@navigator.register(TrendEntity, 'All')
class ShowAllTrends(NavigateStep):
    """Navigate to All Trends screen."""

    VIEW = TrendsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Monitor', 'Trends')


@navigator.register(TrendEntity, 'New')
class AddNewTrend(NavigateStep):
    """Navigate to Create new Trend screen."""

    VIEW = TrendCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(TrendEntity, 'Edit')
class EditTrend(NavigateStep):
    """Navigate to Edit Trend screen.

    Args:
        entity_name: name of the trend
    """

    VIEW = TrendEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.table.row(name=entity_name)['Action'].widget.fill('Edit')
