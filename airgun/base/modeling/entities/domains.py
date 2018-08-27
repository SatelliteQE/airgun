import attr
import sentaku
from navmazing import NavigateToSibling, NavigateToAttribute

from airgun import settings
from airgun.base.application import Application
from airgun.base.application.implementations import AirgunImplementationContext
from airgun.base.modeling import BaseEntity, BaseCollection
from airgun.base.application.implementations.rest_api import RESTAPI
from airgun.base.application.implementations.web_ui import AirgunNavigateStep, WebUI
from airgun.views.domain import (
    DomainCreateView,
    DomainEditView,
    DomainListView,
)


@attr.s
class DomainEntity(BaseEntity, sentaku.modeling.ElementMixin):
    dns_domain = attr.ib()
    full_name = attr.ib(default=None)
    dns_capsule = attr.ib(default=None)
    parameters = attr.ib(default=None)
    locations = attr.ib(default=None)
    organizations = attr.ib(default=None)

    def read(self):
        """Return dict with properties of domain."""
        view = WebUI.navigate_to(self, 'Edit')
        return view.read()

    def update(self, values):
        """Update an existing domain."""
        view = WebUI.navigate_to(self, 'Edit')
        view.fill({
            "domain.dns_domain": values.get("dns_domain"),
            "domain.full_name": values.get("full_name"),
            "domain.dns_capsule": values.get("dns_capsule"),
            "parameters.param": values.get("parameters"),
            "locations.multiselect": values.get("locations"),
            "organizations.multiselect": values.get("organizations")
        })
        view.submit_button.click()
        view.validations.assert_no_errors()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def add_parameter(self, param_name, param_value):
        view = WebUI.navigate_to(self, 'Edit')
        view.parameters.params.add({'name': param_name, 'value': param_value})
        view.submit_button.click()
        view.validations.assert_no_errors()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def remove_parameter(self, param_name):
        view = WebUI.navigate_to(self, 'Edit')
        view.parameters.params.remove(param_name)
        view.submit_button.click()
        view.validations.assert_no_errors()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self):
        view = WebUI.navigate_to(self.application.web_ui, 'Domains')
        self.parent.search(self.dns_domain)
        if not view.table.row_count:
            raise ValueError("Unable to find name '{}'".format(self.dns_domain))
        view.table[0]['Actions'].widget.click()
        self.application.web_ui.widgetastic_browser.handle_alert()
        view.validations.assert_no_errors()
        view.flash.assert_no_error()
        view.flash.dismiss()


@attr.s
class DomainsCollection(BaseCollection, sentaku.modeling.ElementMixin):
    ENTITY = DomainEntity

    create = sentaku.ContextualMethod()

    def search(self, value):
        """Search for 'value' and return domain names that match.

        :param value: text to filter (default: no filter)
        """
        view = WebUI.navigate_to(self.application.web_ui, 'Domains')
        view.search(value)
        return [self.instantiate(row['Description']) for row in view.table.rows()]


@AirgunImplementationContext.external_for(DomainsCollection.create, WebUI)
def create(self, dns_domain, full_name=None, dns_capsule=None, parameters=None, locations=None,
           organizations=None):
    """Create a new domain."""
    view = WebUI.navigate_to(self, 'New')
    view.fill({
        "domain.dns_domain": dns_domain,
        "domain.full_name": full_name,
        "domain.dns_capsule": dns_capsule,
        "parameters.param": parameters,
        "locations.multiselect": locations,
        "organizations.multiselect": organizations
    })
    view.submit_button.click()
    view = self.parent.web_ui.create_view(DomainListView)
    view.validations.assert_no_errors()
    view.flash.assert_no_error()
    view.flash.dismiss()
    return self.instantiate(dns_domain, full_name, dns_capsule, parameters, locations,
                            organizations)


@AirgunImplementationContext.external_for(DomainsCollection.create, RESTAPI)
def create(self, dns_domain, full_name=None, dns_capsule=None, parameters=None, locations=None,
           organizations=None):
    kwargs = {"name": dns_domain}
    if full_name:
        kwargs["fullname"] = full_name
    if dns_capsule:
        kwargs["dns"] = dns_capsule
    if parameters:
        kwargs["domain_parameters_attributes"] = parameters
    if locations:
        kwargs["location"] = locations
    if organizations:
        kwargs["organizations"] = organizations
    server_config = self.application.rest_api.config.ServerConfig(
        auth=(settings.satellite.username, settings.satellite.password),
        url='https://{}'.format(settings.satellite.hostname),
        verify=False
    )
    self.application.rest_api.entities.Domain(
        server_config,
        **kwargs
    ).create(create_missing=True)
    return self.instantiate(dns_domain, full_name, dns_capsule, parameters, locations,
                            organizations)


@WebUI.register_destination_for(WebUI, 'Domains')
class DomainList(AirgunNavigateStep):
    VIEW = DomainListView
    prerequisite = NavigateToSibling("LoggedIn")

    def step(self, *args, **kwargs):
        self.parent.menu.select('Infrastructure', 'Domains')


@WebUI.register_destination_for(DomainsCollection, 'New')
class AddNewDomain(AirgunNavigateStep):
    VIEW = DomainCreateView
    prerequisite = NavigateToAttribute('parent.web_ui', 'Domains')

    def step(self, *args, **kwargs):
        self.parent.create_button.click()


@WebUI.register_destination_for(DomainEntity, 'Edit')
class EditDomain(AirgunNavigateStep):
    VIEW = DomainEditView
    prerequisite = NavigateToAttribute('parent.web_ui', 'Domains')

    def step(self, *args, **kwargs):
        self.parent.search(self.obj.dns_domain)
        row = self.parent.table.row(('Description', self.obj.dns_domain))
        row['Description'].widget.click()
