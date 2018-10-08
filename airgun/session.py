"""Session controller which manages UI session"""
import copy
import logging
import os
import sys
from datetime import datetime

from cached_property import cached_property
from fauxfactory import gen_string

from airgun import settings
from airgun.browser import AirgunBrowser, SeleniumBrowserFactory
from airgun.entities.activationkey import ActivationKeyEntity
from airgun.entities.architecture import ArchitectureEntity
from airgun.entities.computeprofile import ComputeProfileEntity
from airgun.entities.computeresource import ComputeResourceEntity
from airgun.entities.container import ContainerEntity
from airgun.entities.containerimagetag import ContainerImageTagEntity
from airgun.entities.contentcredential import ContentCredentialEntity
from airgun.entities.contenthost import ContentHostEntity
from airgun.entities.contentview import ContentViewEntity
from airgun.entities.dashboard import DashboardEntity
from airgun.entities.discoveredhosts import DiscoveredHostsEntity
from airgun.entities.discoveryrule import DiscoveryRuleEntity
from airgun.entities.domain import DomainEntity
from airgun.entities.errata import ErrataEntity
from airgun.entities.host import HostEntity
from airgun.entities.hostcollection import HostCollectionEntity
from airgun.entities.job_invocation import JobInvocationEntity
from airgun.entities.job_template import JobTemplateEntity
from airgun.entities.filter import FilterEntity
from airgun.entities.ldap_authentication import LDAPAuthenticationEntity
from airgun.entities.lifecycleenvironment import LCEEntity
from airgun.entities.location import LocationEntity
from airgun.entities.login import LoginEntity
from airgun.entities.organization import OrganizationEntity
from airgun.entities.os import OperatingSystemEntity
from airgun.entities.oscapcontent import OSCAPContentEntity
from airgun.entities.oscappolicy import OSCAPPolicyEntity
from airgun.entities.oscaptailoringfile import OSCAPTailoringFileEntity
from airgun.entities.package import PackageEntity
from airgun.entities.partitiontable import PartitionTableEntity
from airgun.entities.puppet_class import PuppetClassEntity
from airgun.entities.puppet_environment import PuppetEnvironmentEntity
from airgun.entities.product import ProductEntity
from airgun.entities.repository import RepositoryEntity
from airgun.entities.rhai.action import ActionEntity
from airgun.entities.rhai.inventory import InventoryHostEntity
from airgun.entities.rhai.manage import ManageEntity
from airgun.entities.rhai.overview import OverviewEntity
from airgun.entities.rhai.plan import PlanEntity
from airgun.entities.rhai.rule import RuleEntity
from airgun.entities.role import RoleEntity
from airgun.entities.task import TaskEntity
from airgun.entities.template import ProvisioningTemplateEntity
from airgun.entities.smart_class_parameter import SmartClassParameterEntity
from airgun.entities.smart_variable import SmartVariableEntity
from airgun.entities.subnet import SubnetEntity
from airgun.entities.syncplan import SyncPlanEntity
from airgun.entities.sync_status import SyncStatusEntity
from airgun.entities.user import UserEntity
from airgun.entities.usergroup import UserGroupEntity
from airgun.navigation import navigator

LOGGER = logging.getLogger(__name__)


class Session(object):
    """A session context manager which is a key controller in airgun.

    It is responsible for initializing and starting
    :class:`airgun.browser.AirgunBrowser`, navigating to satellite, performing
    post-init browser tweaks, initializing navigator, all available UI
    entities, and logging in to satellite.

    When session is about to close, it saves a screenshot in case of any
    exception, attempts to log out from satellite and performs all necessary
    browser closure steps like quitting the browser, sending results to
    saucelabs, stopping docker container etc.

    For tests level it offers direct control over when UI session is started
    and stopped as well as provides all the entities available without the need
    to import and initialize them manually.

    Usage::

        def test_foo():
            # steps executed before starting UI session
            # [...]

            # start of UI session
            with Session('test_foo') as session:
                # steps executed during UI session. For example:
                session.architecture.create({'name': 'bar'})
                [...]

            # steps executed after UI session was closed

    You can also pass credentials different from default ones specified in
    settings like that::

        with Session(test_name, user='foo', password='bar'):
            # [...]

    Every test may use multiple sessions if needed::

        def test_foo():
            with Session('test_foo', 'admin', 'password') as admin_session:
                # UI steps, performed by 'admin' user
                admin_session.user.create({'login': 'user1', 'password: 'pwd'})
                # [...]
            with Session('test_foo', 'user1', 'pwd1') as user1_session:
                # UI steps, performed by 'user1' user
                user1_session.architecture.create({'name': 'bar'})
                # [...]

    Nested sessions are supported as well, just don't forget to use different
    variables for sessions::

        def test_foo():
            with Session('test_foo', 'admin', 'password') as admin_session:
                # UI steps, performed by 'admin' user only
                admin_session.user.create({'login': 'user1', 'password: 'pwd'})
                # [...]
                with Session('test_foo', 'user1', 'pwd1') as user1_session:
                    # UI steps, performed by 'user1' user OR 'admin' in
                    # different browser instances
                    user1_session.architecture.create({'name': 'bar'})
                    admin_session.architecture.search('bar')
                    # [...]
                # UI steps, performed by 'admin' user only
                admin_session.user.delete({'login': 'user1'})

    """

    def __init__(self, session_name=None, user=None, password=None):
        """Stores provided values, doesn't perform any actions.

        :param str optional session_name: string representing session name.
            Used in screenshot names, saucelabs test results, docker container
            names etc. You should provide your test name here in most cases.
            Defaults to random alphanumeric value.
        :param str optional user: username (login) of user, who will perform UI
            actions. If None is passed - default one provided by settings will
            beused.
        :param str optional password: password for provided user. If None is
            passed - default one from settings will be used.
        """
        self.name = session_name or gen_string('alphanumeric')
        self._user = user or settings.satellite.username
        self._password = password or settings.satellite.password
        self._factory = None
        self.browser = None

    def __enter__(self):
        """Starts the browser, navigates to satellite, performs post-init
        browser tweaks, initializes navigator and UI entities, and logs in to
        satellite.
        """
        LOGGER.info(
            u'Starting UI session %r for user %r', self.name, self._user)
        self._factory = SeleniumBrowserFactory(test_name=self.name)
        try:
            selenium_browser = self._factory.get_browser()
            self.browser = AirgunBrowser(selenium_browser, self)

            self.browser.url = 'https://' + settings.satellite.hostname
            self._factory.post_init()

            # Navigator
            self.navigator = copy.deepcopy(navigator)
            self.navigator.browser = self.browser

            self.login.login({
                'username': self._user, 'password': self._password})
        except Exception as exception:
            self.__exit__(*sys.exc_info())
            raise exception
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Attempts to log out, saves the screenshot and performs all required
        session closure activities.

        NOTE: exceptions during logout or saving screenshot are just logged and
            not risen not to shadow real session result.
        """
        LOGGER.info(
            u'Stopping UI session %r for user %r', self.name, self._user)
        passed = True if exc_type is None else False
        try:
            if passed:
                self.login.logout()
            else:
                self.take_screenshot()
        except Exception as err:
            LOGGER.exception(err)
        finally:
            self._factory.finalize(passed)

    def take_screenshot(self):
        """Take screen shot from the current browser window.

        The screenshot named ``screenshot-YYYY-mm-dd_HH_MM_SS.png`` will be
        placed on the path specified by
        ``settings.screenshots_path/YYYY-mm-dd/ClassName/method_name/``.

        All directories will be created if they don't exist. Make sure that the
        user running Robottelo have the right permissions to create files and
        directories matching the complete.

        This method is called automatically in case any exception during UI
        session happens.
        """
        now = datetime.now()
        path = os.path.join(
            settings.selenium.screenshots_path,
            now.strftime('%Y-%m-%d'),
        )
        if not os.path.exists(path):
            os.makedirs(path)
        filename = '{0}-screenshot-{1}.png'.format(
            self.name.replace(' ', '_'),
            now.strftime('%Y-%m-%d_%H_%M_%S')
        )
        path = os.path.join(path, filename)
        LOGGER.debug('Saving screenshot %s', path)
        self.browser.selenium.save_screenshot(path)

    @cached_property
    def activationkey(self):
        """Instance of Activation Key entity."""
        return ActivationKeyEntity(self.browser)

    @cached_property
    def architecture(self):
        """Instance of Architecture entity."""
        return ArchitectureEntity(self.browser)

    @cached_property
    def computeprofile(self):
        """Instance of Compute Profile entity."""
        return ComputeProfileEntity(self.browser)

    @cached_property
    def container(self):
        """Instance of Container entity."""
        return ContainerEntity(self.browser)

    @cached_property
    def containerimagetag(self):
        """Instance of Container Image Tags entity."""
        return ContainerImageTagEntity(self.browser)

    @cached_property
    def contentcredential(self):
        """Instance of Content Credential entity."""
        return ContentCredentialEntity(self.browser)

    @cached_property
    def contenthost(self):
        """Instance of Content Host entity."""
        return ContentHostEntity(self.browser)

    @cached_property
    def computeresource(self):
        """Instance of ComputeResource entity."""
        return ComputeResourceEntity(self.browser)

    @cached_property
    def contentview(self):
        """Instance of Content View entity."""
        return ContentViewEntity(self.browser)

    @cached_property
    def dashboard(self):
        """Instance of Dashboard entity."""
        return DashboardEntity(self.browser)

    @cached_property
    def discoveredhosts(self):
        return DiscoveredHostsEntity(self.browser)

    @cached_property
    def discoveryrule(self):
        """Instance of Discovery Rule entity."""
        return DiscoveryRuleEntity(self.browser)

    @cached_property
    def domain(self):
        """Instance of domain entity."""
        return DomainEntity(self.browser)

    @cached_property
    def errata(self):
        """Instance of Errata entity."""
        return ErrataEntity(self.browser)

    @cached_property
    def filter(self):
        """Instance of Filter entity."""
        return FilterEntity(self.browser)

    @cached_property
    def host(self):
        """Instance of Host entity."""
        return HostEntity(self.browser)

    @cached_property
    def hostcollection(self):
        """Instance of Host Collection entity."""
        return HostCollectionEntity(self.browser)

    @cached_property
    def insightsaction(self):
        """Instance of RHAI Action entity."""
        return ActionEntity(self.browser)

    @cached_property
    def insightsinventory(self):
        """Instance of RHAI Inventory entity."""
        return InventoryHostEntity(self.browser)

    @cached_property
    def insightsoverview(self):
        """Instance of RHAI Overview entity."""
        return OverviewEntity(self.browser)

    @cached_property
    def insightsplan(self):
        """Instance of RHAI Plan entity."""
        return PlanEntity(self.browser)

    @cached_property
    def insightsrule(self):
        """Instance of RHAI Rule entity."""
        return RuleEntity(self.browser)

    @cached_property
    def jobinvocation(self):
        """Instance of Job Invocation entity."""
        return JobInvocationEntity(self.browser)

    @cached_property
    def insightsmanage(self):
        """Instance of RHAI Manage entity."""
        return ManageEntity(self.browser)

    @cached_property
    def jobtemplate(self):
        """Instance of Job Template entity."""
        return JobTemplateEntity(self.browser)

    @cached_property
    def ldapauthentication(self):
        """Instance of LDAP Authentication entity."""
        return LDAPAuthenticationEntity(self.browser)

    @cached_property
    def lifecycleenvironment(self):
        """Instance of LCE entity."""
        return LCEEntity(self.browser)

    @cached_property
    def location(self):
        """Instance of Location entity."""
        return LocationEntity(self.browser)

    @cached_property
    def login(self):
        """Instance of Login entity."""
        return LoginEntity(self.browser)

    @cached_property
    def operatingsystem(self):
        """Instance of Operating System entity."""
        return OperatingSystemEntity(self.browser)

    @cached_property
    def organization(self):
        """Instance of Organization entity."""
        return OrganizationEntity(self.browser)

    @cached_property
    def oscapcontent(self):
        """Instance of OSCAP Content entity."""
        return OSCAPContentEntity(self.browser)

    @cached_property
    def oscappolicy(self):
        """Instance of OSCAP Policy entity."""
        return OSCAPPolicyEntity(self.browser)

    @cached_property
    def oscaptailoringfile(self):
        """Instance of OSCAP Tailoring File entity."""
        return OSCAPTailoringFileEntity(self.browser)

    @cached_property
    def package(self):
        """Instance of Packge entity."""
        return PackageEntity(self.browser)

    @cached_property
    def partitiontable(self):
        """Instance of Partition Table entity."""
        return PartitionTableEntity(self.browser)

    @cached_property
    def puppetclass(self):
        """Instance of Puppet Class entity."""
        return PuppetClassEntity(self.browser)

    @cached_property
    def puppetenvironment(self):
        """Instance of Puppet Environment entity."""
        return PuppetEnvironmentEntity(self.browser)

    @cached_property
    def product(self):
        """Instance of Product entity."""
        return ProductEntity(self.browser)

    @cached_property
    def provisioningtemplate(self):
        """Instance of Provisioning Template entity."""
        return ProvisioningTemplateEntity(self.browser)

    @cached_property
    def repository(self):
        """Instance of Repository entity."""
        return RepositoryEntity(self.browser)

    @cached_property
    def role(self):
        """Instance of Role entity."""
        return RoleEntity(self.browser)

    @cached_property
    def sc_parameter(self):
        """Instance of Smart Class Parameter entity."""
        return SmartClassParameterEntity(self.browser)

    @cached_property
    def smartvariable(self):
        """Instance of Smart Variable entity."""
        return SmartVariableEntity(self.browser)

    @cached_property
    def subnet(self):
        """Instance of Subnet entity."""
        return SubnetEntity(self.browser)

    @cached_property
    def syncplan(self):
        """Instance of Sync Plan entity."""
        return SyncPlanEntity(self.browser)

    @cached_property
    def sync_status(self):
        """Instance of Sync Status entity"""
        return SyncStatusEntity(self.browser)

    @cached_property
    def task(self):
        """Instance of Task entity."""
        return TaskEntity(self.browser)

    @cached_property
    def user(self):
        """Instance of User entity."""
        return UserEntity(self.browser)

    @cached_property
    def usergroup(self):
        """Instance of User Group entity."""
        return UserGroupEntity(self.browser)
