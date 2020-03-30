"""Session controller which manages UI session"""
import logging
import os
import sys
from datetime import datetime

from cached_property import cached_property
from fauxfactory import gen_string

from airgun import settings
from airgun.browser import AirgunBrowser
from airgun.browser import SeleniumBrowserFactory
from airgun.entities.activationkey import ActivationKeyEntity
from airgun.entities.architecture import ArchitectureEntity
from airgun.entities.audit import AuditEntity
from airgun.entities.bookmark import BookmarkEntity
from airgun.entities.computeprofile import ComputeProfileEntity
from airgun.entities.computeresource import ComputeResourceEntity
from airgun.entities.configgroup import ConfigGroupEntity
from airgun.entities.containerimagetag import ContainerImageTagEntity
from airgun.entities.contentcredential import ContentCredentialEntity
from airgun.entities.contenthost import ContentHostEntity
from airgun.entities.contentview import ContentViewEntity
from airgun.entities.contentviewfilter import ContentViewFilterEntity
from airgun.entities.dashboard import DashboardEntity
from airgun.entities.discoveredhosts import DiscoveredHostsEntity
from airgun.entities.discoveryrule import DiscoveryRuleEntity
from airgun.entities.domain import DomainEntity
from airgun.entities.errata import ErrataEntity
from airgun.entities.filter import FilterEntity
from airgun.entities.hardware_model import HardwareModelEntity
from airgun.entities.host import HostEntity
from airgun.entities.hostcollection import HostCollectionEntity
from airgun.entities.hostgroup import HostGroupEntity
from airgun.entities.http_proxy import HTTPProxyEntity
from airgun.entities.job_invocation import JobInvocationEntity
from airgun.entities.job_template import JobTemplateEntity
from airgun.entities.ldap_authentication import LDAPAuthenticationEntity
from airgun.entities.lifecycleenvironment import LCEEntity
from airgun.entities.location import LocationEntity
from airgun.entities.login import LoginEntity
from airgun.entities.media import MediaEntity
from airgun.entities.modulestream import ModuleStreamEntity
from airgun.entities.organization import OrganizationEntity
from airgun.entities.os import OperatingSystemEntity
from airgun.entities.oscapcontent import OSCAPContentEntity
from airgun.entities.oscappolicy import OSCAPPolicyEntity
from airgun.entities.oscaptailoringfile import OSCAPTailoringFileEntity
from airgun.entities.package import PackageEntity
from airgun.entities.partitiontable import PartitionTableEntity
from airgun.entities.product import ProductEntity
from airgun.entities.provisioning_template import ProvisioningTemplateEntity
from airgun.entities.puppet_class import PuppetClassEntity
from airgun.entities.puppet_environment import PuppetEnvironmentEntity
from airgun.entities.redhat_repository import RedHatRepositoryEntity
from airgun.entities.report_template import ReportTemplateEntity
from airgun.entities.repository import RepositoryEntity
from airgun.entities.rhai.action import ActionEntity
from airgun.entities.rhai.inventory import InventoryHostEntity
from airgun.entities.rhai.manage import ManageEntity
from airgun.entities.rhai.overview import OverviewEntity
from airgun.entities.rhai.plan import PlanEntity
from airgun.entities.rhai.rule import RuleEntity
from airgun.entities.rhsso_login import RHSSOLoginEntity
from airgun.entities.role import RoleEntity
from airgun.entities.settings import SettingsEntity
from airgun.entities.smart_class_parameter import SmartClassParameterEntity
from airgun.entities.smart_variable import SmartVariableEntity
from airgun.entities.subnet import SubnetEntity
from airgun.entities.subscription import SubscriptionEntity
from airgun.entities.sync_status import SyncStatusEntity
from airgun.entities.sync_templates import SyncTemplatesEntity
from airgun.entities.syncplan import SyncPlanEntity
from airgun.entities.task import TaskEntity
from airgun.entities.trend import TrendEntity
from airgun.entities.user import UserEntity
from airgun.entities.usergroup import UserGroupEntity
from airgun.entities.virtwho_configure import VirtwhoConfigureEntity
from airgun.navigation import Navigate
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

    def __init__(self, session_name=None, user=None, password=None,
                 session_cookie=None, url=None, login=True):
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
        :param requests.sessions.Session optional session_cookie: session object to be used
            to bypass login
        :param str optional url: URL path to open when starting session (without protocol
            and hostname)
        """
        self.name = session_name or gen_string('alphanumeric')
        self._user = user or settings.satellite.username
        self._password = password or settings.satellite.password
        self._session_cookie = session_cookie
        self._factory = None
        self._url = url
        self.navigator = None
        self.browser = None
        self._login = login

    def __call__(self, user=None, password=None, session_cookie=None, url=None, login=None):
        """Stores provided values. This allows tests to provide additional
        value when Session object is returned from fixture and used as
        context manager. Arguments are the same as when initializing
        Session object, except session_name.
        """
        if user is not None:
            self._user = user
        if password is not None:
            self._password = password
        if session_cookie is not None:
            self._session_cookie = session_cookie
        if url is not None:
            self._url = url
        if login is not None:
            self._login = login
        return self

    def __enter__(self):
        """Just a shim to make it compatible with context manager
        protocol. The real work is done by _open the first time
        any entity is requested.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Attempts to log out, saves the screenshot and performs all required
        session closure activities.

        NOTE: exceptions during logout or saving screenshot are just logged and
            not risen not to shadow real session result.
        """
        if self.browser is None:
            # browser was never started, don't do anything
            return
        LOGGER.info(
            u'Stopping UI session %r for user %r', self.name, self._user)
        passed = True if exc_type is None else False
        try:
            if not passed:
                self.take_screenshot()
        except Exception as err:
            LOGGER.exception(err)
        finally:
            self._factory.finalize(passed)

    def _open(self, entity):
        """Initializes requested entity. If this is first time session
        requests an entity, also initialize and prepare browser.
        """
        if self.browser is None:
            if self._url:
                endpoint = self._url
            else:
                endpoint = getattr(entity, 'endpoint_path', '/')
            full_url = f"https://{settings.satellite.hostname}{endpoint}"
            self._prepare_browser(full_url)

        return entity(self.browser)

    def _prepare_browser(self, url):
        """Starts the browser, navigates to satellite, performs post-init
        browser tweaks, initializes navigator and UI entities, and logs in to
        satellite.
        """
        if self._session_cookie:
            LOGGER.info('Starting UI session id: %r from a session cookie',
                        self._session_cookie.cookies.get_dict()['_session_id'])
        else:
            LOGGER.info('Starting UI session %r for user %r', self.name, self._user)
        self._factory = SeleniumBrowserFactory(
            test_name=self.name,
            session_cookie=self._session_cookie
        )
        try:
            selenium_browser = self._factory.get_browser()
            self.browser = AirgunBrowser(selenium_browser, self)
            LOGGER.info('Setting initial URL to {url}')

            self.browser.url = url

            self._factory.post_init()

            # Navigator
            self.navigator = Navigate(self.browser)
            self.navigator.dest_dict = navigator.dest_dict.copy()
            if self._session_cookie is None and self._login:
                self.login.login({
                    'username': self._user, 'password': self._password})
        except Exception as exception:
            self.__exit__(*sys.exc_info())
            raise exception

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
        return self._open(ActivationKeyEntity)

    @cached_property
    def architecture(self):
        """Instance of Architecture entity."""
        return self._open(ArchitectureEntity)

    @cached_property
    def audit(self):
        """Instance of Audit entity."""
        return self._open(AuditEntity)

    @cached_property
    def bookmark(self):
        """Instance of Bookmark entity."""
        return self._open(BookmarkEntity)

    @cached_property
    def computeprofile(self):
        """Instance of Compute Profile entity."""
        return self._open(ComputeProfileEntity)

    @cached_property
    def configgroup(self):
        """Instance of Config Group entity."""
        return self._open(ConfigGroupEntity)

    @cached_property
    def containerimagetag(self):
        """Instance of Container Image Tags entity."""
        return self._open(ContainerImageTagEntity)

    @cached_property
    def contentcredential(self):
        """Instance of Content Credential entity."""
        return self._open(ContentCredentialEntity)

    @cached_property
    def contenthost(self):
        """Instance of Content Host entity."""
        return self._open(ContentHostEntity)

    @cached_property
    def computeresource(self):
        """Instance of ComputeResource entity."""
        return self._open(ComputeResourceEntity)

    @cached_property
    def contentview(self):
        """Instance of Content View entity."""
        return self._open(ContentViewEntity)

    @cached_property
    def contentviewfilter(self):
        """Instance of Content View Filter entity."""
        return self._open(ContentViewFilterEntity)

    @cached_property
    def dashboard(self):
        """Instance of Dashboard entity."""
        return self._open(DashboardEntity)

    @cached_property
    def discoveredhosts(self):
        return self._open(DiscoveredHostsEntity)

    @cached_property
    def discoveryrule(self):
        """Instance of Discovery Rule entity."""
        return self._open(DiscoveryRuleEntity)

    @cached_property
    def domain(self):
        """Instance of domain entity."""
        return self._open(DomainEntity)

    @cached_property
    def errata(self):
        """Instance of Errata entity."""
        return self._open(ErrataEntity)

    @cached_property
    def filter(self):
        """Instance of Filter entity."""
        return self._open(FilterEntity)

    @cached_property
    def hardwaremodel(self):
        """Instance of Hardware Model entity."""
        return self._open(HardwareModelEntity)

    @cached_property
    def host(self):
        """Instance of Host entity."""
        return self._open(HostEntity)

    @cached_property
    def hostcollection(self):
        """Instance of Host Collection entity."""
        return self._open(HostCollectionEntity)

    @cached_property
    def hostgroup(self):
        """Instance of Host Group entity."""
        return self._open(HostGroupEntity)

    @cached_property
    def http_proxy(self):
        """Instance of HTTP Proxy entity."""
        return self._open(HTTPProxyEntity)

    @cached_property
    def insightsaction(self):
        """Instance of RHAI Action entity."""
        return self._open(ActionEntity)

    @cached_property
    def insightsinventory(self):
        """Instance of RHAI Inventory entity."""
        return self._open(InventoryHostEntity)

    @cached_property
    def insightsoverview(self):
        """Instance of RHAI Overview entity."""
        return self._open(OverviewEntity)

    @cached_property
    def insightsplan(self):
        """Instance of RHAI Plan entity."""
        return self._open(PlanEntity)

    @cached_property
    def insightsrule(self):
        """Instance of RHAI Rule entity."""
        return self._open(RuleEntity)

    @cached_property
    def jobinvocation(self):
        """Instance of Job Invocation entity."""
        return self._open(JobInvocationEntity)

    @cached_property
    def insightsmanage(self):
        """Instance of RHAI Manage entity."""
        return self._open(ManageEntity)

    @cached_property
    def jobtemplate(self):
        """Instance of Job Template entity."""
        return self._open(JobTemplateEntity)

    @cached_property
    def ldapauthentication(self):
        """Instance of LDAP Authentication entity."""
        return self._open(LDAPAuthenticationEntity)

    @cached_property
    def lifecycleenvironment(self):
        """Instance of LCE entity."""
        return self._open(LCEEntity)

    @cached_property
    def location(self):
        """Instance of Location entity."""
        return self._open(LocationEntity)

    @cached_property
    def login(self):
        """Instance of Login entity."""
        return self._open(LoginEntity)

    @cached_property
    def operatingsystem(self):
        """Instance of Operating System entity."""
        return self._open(OperatingSystemEntity)

    @cached_property
    def organization(self):
        """Instance of Organization entity."""
        return self._open(OrganizationEntity)

    @cached_property
    def oscapcontent(self):
        """Instance of OSCAP Content entity."""
        return self._open(OSCAPContentEntity)

    @cached_property
    def oscappolicy(self):
        """Instance of OSCAP Policy entity."""
        return self._open(OSCAPPolicyEntity)

    @cached_property
    def oscaptailoringfile(self):
        """Instance of OSCAP Tailoring File entity."""
        return self._open(OSCAPTailoringFileEntity)

    @cached_property
    def package(self):
        """Instance of Packge entity."""
        return self._open(PackageEntity)

    @cached_property
    def media(self):
        """Instance of Media entity."""
        return self._open(MediaEntity)

    @cached_property
    def modulestream(self):
        """Instance of Module Stream entity."""
        return self._open(ModuleStreamEntity)

    @cached_property
    def partitiontable(self):
        """Instance of Partition Table entity."""
        return self._open(PartitionTableEntity)

    @cached_property
    def puppetclass(self):
        """Instance of Puppet Class entity."""
        return self._open(PuppetClassEntity)

    @cached_property
    def puppetenvironment(self):
        """Instance of Puppet Environment entity."""
        return self._open(PuppetEnvironmentEntity)

    @cached_property
    def product(self):
        """Instance of Product entity."""
        return self._open(ProductEntity)

    @cached_property
    def provisioningtemplate(self):
        """Instance of Provisioning Template entity."""
        return self._open(ProvisioningTemplateEntity)

    @cached_property
    def reporttemplate(self):
        """Instance of Report Template entity."""
        return self._open(ReportTemplateEntity)

    @cached_property
    def redhatrepository(self):
        """Instance of Red Hat Repository entity."""
        return self._open(RedHatRepositoryEntity)

    @cached_property
    def repository(self):
        """Instance of Repository entity."""
        return self._open(RepositoryEntity)

    @cached_property
    def role(self):
        """Instance of Role entity."""
        return self._open(RoleEntity)

    @cached_property
    def rhsso_login(self):
        """Instance of RHSSOLoginEntity entity."""
        return self._open(RHSSOLoginEntity)

    @cached_property
    def settings(self):
        """Instance of Settings entity."""
        return self._open(SettingsEntity)

    @cached_property
    def sc_parameter(self):
        """Instance of Smart Class Parameter entity."""
        return self._open(SmartClassParameterEntity)

    @cached_property
    def smartvariable(self):
        """Instance of Smart Variable entity."""
        return self._open(SmartVariableEntity)

    @cached_property
    def subnet(self):
        """Instance of Subnet entity."""
        return self._open(SubnetEntity)

    @cached_property
    def subscription(self):
        """Instance of Subscription entity."""
        return self._open(SubscriptionEntity)

    @cached_property
    def syncplan(self):
        """Instance of Sync Plan entity."""
        return self._open(SyncPlanEntity)

    @cached_property
    def sync_status(self):
        """Instance of Sync Status entity"""
        return self._open(SyncStatusEntity)

    @cached_property
    def sync_template(self):
        """Instance of Sync Templates entity"""
        return self._open(SyncTemplatesEntity)

    @cached_property
    def task(self):
        """Instance of Task entity."""
        return self._open(TaskEntity)

    @cached_property
    def trend(self):
        """Instance of Trend entity."""
        return self._open(TrendEntity)

    @cached_property
    def user(self):
        """Instance of User entity."""
        return self._open(UserEntity)

    @cached_property
    def usergroup(self):
        """Instance of User Group entity."""
        return self._open(UserGroupEntity)

    @cached_property
    def virtwho_configure(self):
        """Instance of Virtwho Configure entity."""
        return self._open(VirtwhoConfigureEntity)
