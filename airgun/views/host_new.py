from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic.widget import Widget
from widgetastic_patternfly4 import Tab
from widgetastic_patternfly4.ouia import BreadCrumb
from widgetastic_patternfly4.ouia import Button
from widgetastic_patternfly4.ouia import Dropdown

from airgun.views.common import BaseLoggedInView


class Card(View):
    """Each card in host view has it's own title with same locator"""

    title = Text('.//div[@class="pf-c-card__title"]')


class HostDetailsCard(Widget):
    """Details card body contains multiple host detail information"""

    LABELS = './/div[@class="pf-c-description-list__group"]//dt//span'
    VALUES = './/div[@class="pf-c-description-list__group"]//dd//descendant::*/text()/..'

    def read(self):
        """Return a dictionary where keys are property names and values are property values.
        Values are either in span elements or in div elements
        """
        items = {}
        labels = self.browser.elements(self.LABELS)
        values = self.browser.elements(self.VALUES)
        # the length of elements should be always same
        if len(values) != len(labels):
            raise AttributeError(
                'Each label should have one value, therefore length should be equal. '
                f'But length of labels: {len(labels)} is not equal to length of {len(values)}, '
                'Please double check xpaths.'
            )
        for key, value in zip(labels, values):
            value = self.browser.text(value)
            key = self.browser.text(key).replace(' ', '_').lower()
            items[key] = value
        return items


class NewHostDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb('OUIA-Generated-Breadcrumb-1')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return breadcrumb_loaded and self.breadcrumb.locations[0] == 'Hosts'

    edit = Button('OUIA-Generated-Button-secondary-1')
    dropdown = Dropdown('OUIA-Generated-Dropdown-2')

    @View.nested
    class Overview(Tab):
        ROOT = './/div[contains(@class, "host-details-tab-item")]'

        @View.nested
        class DetailsCard(Card):
            ROOT = '(.//article[contains(@class, "pf-c-card")])[1]'
            details = HostDetailsCard()

        @View.nested
        class HostStatusCard(Card):
            ROOT = '(//article[contains(@class, "pf-c-card")])[2]'
            status = Text('.//h4[contains(@data-ouia-component-id, "OUIA-Generated-Title")]')

            status_success = Text('.//span[@class="status-success"]')
            status_warning = Text('.//span[@class="status-warning"]')
            status_error = Text('.//span[@class="status-error"]')
            status_disabled = Text('.//span[@class="disabled"]')

    @View.nested
    class Content(Tab):
        pass

    @View.nested
    class Traces(Tab):
        enable_traces = Button('Enable Traces')

    @View.nested
    class RepositorySets(Tab):
        pass

    @View.nested
    class Ansible(Tab):
        pass

    @View.nested
    class Insights(Tab):
        pass
