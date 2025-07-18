from widgetastic.widget import Text, View
from widgetastic_patternfly4 import Button
from widgetastic_patternfly5.ouia import FormSelect as PF5FormSelect

from airgun.views.common import BaseLoggedInView, SearchableViewMixin, WizardStepView
from airgun.widgets import (
    ActionsDropdown,
    SatTable,
)


class SCAPReportView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[normalize-space(.)='Compliance Reports']")
    table = SatTable(
        './/table',
        column_widgets={
            'Host': Text(".//a[contains(@href,'/new/hosts')]"),
            'Reported At': Text(".//a[contains(@href,'/compliance/arf_reports')]"),
            'Policy': Text(".//a[contains(@href,'/compliance/policies')]"),
            'Openscap Capsule': Text(".//a[contains(@href,'/smart_proxies')]"),
            'Passed': Text(".//span[contains(@class,'label-info')]"),
            'Failed': Text(".//span[contains(@class,'label-danger')]"),
            'Other': Text(".//span[contains(@class,'label-warning')]"),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class SCAPReportDetailsView(BaseLoggedInView):
    show_log_messages_label = Text('//span[normalize-space(.)="Show log messages:"]')
    table = SatTable(
        './/table',
        column_widgets={
            'Result': Text('./span[1]'),
            'Message': Text('./span[2]'),
            'Resource': Text('./span[3]'),
            'Severity': Text('./img[1]'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        },
    )

    @property
    def is_displayed(self):
        return (
            self.browser.wait_for_element(self.show_log_messages_label, exception=False) is not None
        )


class RemediateModal(View):
    """
    Class representing the "Remediate" modal.
    It contains multiple nested classes each representing a step of the wizard.
    """

    ROOT = '//div[contains(@data-ouia-component-id, "OUIA-Generated-Modal-large-")]'

    title = Text('.//h2[contains(@class, "pf-v5-c-wizard__title-text")]')
    close_modal = Button(locator='.//button[@aria-label="Close"]')

    @View.nested
    class select_remediation_method(WizardStepView):
        expander = Text(
            './/button[contains(@class,"pf-v5-c-wizard__nav-link") and contains(.,"Select snippet")]'
        )
        snippet = PF5FormSelect('snippet-select')

    @View.nested
    class name_source(WizardStepView):
        expander = Text(
            './/button[contains(@class,"pf-v5-c-wizard__nav-link") and contains(.,"Review hosts")]'
        )
        host_table = SatTable(".//table")

    @View.nested
    class select_capsule(WizardStepView):
        expander = Text(
            './/button[contains(@class,"pf-v5-c-wizard__nav-link") and contains(.,"Review remediation")]'
        )
        run = Button(locator='.//button[normalize-space(.)="Run"]')
