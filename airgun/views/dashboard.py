from widgetastic.widget import Table
from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic.widget import Widget

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SatTable
from airgun.widgets import ActionsDropdown
from airgun.widgets import PieChart
from airgun.widgets import Search


class ItemValueList(Widget):
    """List of name-value pairs. Each name element from every pair is clickable

    Example html representation::

        <ul>
            <li>
                <a class="dashboard-links"...>Hosts with no reports</a>
                <h4>5</h4>
            </li>
    """

    LABELS = ".//li/a[@class='dashboard-links']"
    LABEL = ".//li/a[@class='dashboard-links'][normalize-space(.)='{}']"
    VALUE = ".//h4[preceding-sibling::a[contains(., '{}')]]"

    def read(self):
        """Return a dictionary where keys are widget criteria names and
        values are number of hosts that correspond to these criteria
        """
        values = {}
        for item in self.browser.elements(self.LABELS):
            name = self.browser.text(item)
            value = int(self.browser.text(self.VALUE.format(name)))
            values[name] = value
        return values

    def fill(self, value):
        """Click on specific criteria from the widget list"""
        self.browser.click(self.browser.element(self.LABEL.format(value)))


class TotalCount(Widget):
    """Return total hosts count from Host Configuration Status type of
    widgets
    """

    total_count = Text(".//h4[@class='total']")

    def read(self):
        """Return hosts count from widget. Usually it is a string like
        'Total Hosts: 5'
        """
        _, _, count = self.total_count.read().partition(':')
        return int(count)


class AutoRefresh(Widget):
    """Widget refer to auto refresh functionality on dashboard"""

    AUTO_REFRESH = "//a[contains(@href, '/?auto_refresh')]"

    def read(self):
        """Return whether functionality is enabled or disabled"""
        if (
            self.browser.element(self.AUTO_REFRESH).get_attribute('data-original-title')
            == 'Auto refresh on'
        ):
            return True
        return False

    def fill(self, value):
        """Click on a button if state of the widget need to be changed"""
        if self.read() != value:
            self.browser.element(self.AUTO_REFRESH).click()


class DashboardView(BaseLoggedInView):
    title = Text("//h1[text()='Overview']")
    manage = ActionsDropdown("//div[@class='btn-group']")
    refresh = AutoRefresh()
    searchbox = Search()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None

    def search(self, query):
        """Return whole dashboard view as a result of a search

        :param str query: search query to type into search field.
        :return: all view widgets values
        :rtype: dict
        """
        self.searchbox.search(query)
        return self.read()

    @View.nested
    class DiscoveredHosts(View):
        ROOT = ".//li[@data-name='Discovered Hosts']"
        hosts = Table('.//table')
        hosts_count = Text(".//a[@data-id='aid_discovered_hosts']")

    @View.nested
    class HostConfigurationStatus(View):
        ROOT = ".//li[@data-name='Host Configuration Status for All']"
        status_list = ItemValueList()
        total_count = TotalCount()

    @View.nested
    class TaskStatus(View):
        ROOT = ".//li[@data-name='Task Status']"
        states = SatTable(
            './/table',
            column_widgets={'No. of Tasks': Text('./a')},
        )

        def fill(self, values):
            if 'state' not in values or 'result' not in values:
                raise ValueError('both state and result values have to be provided')
            self.states.row(state=values['state'], result=values['result'])[
                'No. of Tasks'
            ].widget.click()

    @View.nested
    class LatestJobs(View):
        ROOT = ".//li[@data-name='Latest Jobs']"
        jobs = SatTable('.//table')

    @View.nested
    class HostConfigurationChart(View):
        ROOT = ".//li[@data-name='Host Configuration Chart for All']"
        chart = PieChart(".//div[@class='host-configuration-chart']")

    @View.nested
    class ContentViews(View):
        ROOT = ".//li[@data-name='Content Views']"
        content_views = SatTable('.//table', column_widgets={'Content View': Text('./a')})

    @View.nested
    class SyncOverview(View):
        ROOT = ".//li[@data-name='Sync Overview']"
        syncs = Table('.//table')

    @View.nested
    class HostSubscription(View):
        ROOT = ".//li[@data-name='Host Subscription Status']"
        subscriptions = SatTable('.//table', column_widgets={0: Text('./a')})

        def fill(self, values):
            if 'type' not in values:
                raise ValueError('You need provide subscription task type')
            self.subscriptions.row((0, 'contains', str(values['type'])))[0].widget.click()

    @View.nested
    class SubscriptionStatus(View):
        ROOT = ".//li[@data-name='Subscription Status']"
        subscriptions = SatTable('.//table')

    @View.nested
    class LatestErrata(View):
        ROOT = ".//li[@data-name='Latest Errata']"
        erratas = SatTable('.//table')

    @View.nested
    class NewHosts(View):
        ROOT = ".//li[@data-name='New Hosts']"
        hosts = Table('.//table')

    @View.nested
    class HostCollections(View):
        ROOT = ".//li[@data-name='Host Collections']"
        collections = SatTable('.//table')

    @View.nested
    class LatestFailedTasks(View):
        ROOT = ".//li[@data-name='Latest Warning/Error Tasks']"
        tasks = SatTable('.//table', column_widgets={'Name': Text('./a')})

        def fill(self, values):
            if 'name' not in values:
                raise ValueError('You need provide name of the task')
            self.tasks.row(name=values['name'])['Name'].widget.click()

    @View.nested
    class VirtWhoConfigStatus(View):
        ROOT = ".//li[@data-name='Virt-who Configs Status']"
        config_status = Table('.//table')
        latest_config = Text(".//div[@class='ca']")
