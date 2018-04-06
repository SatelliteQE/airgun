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
from airgun.entities.login import LoginEntity
from airgun.entities.activationkey import ActivationKeyEntity
from airgun.entities.architecture import ArchitectureEntity
from airgun.entities.contentview import ContentViewEntity
from airgun.entities.hostcollection import HostCollectionEntity
from airgun.entities.location import LocationEntity
from airgun.entities.os import OperatingSystemEntity
from airgun.entities.organization import OrganizationEntity
from airgun.entities.subnet import SubnetEntity
from airgun.entities.syncplan import SyncPlanEntity


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
            selenium_browser.maximize_window()
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
    def contentview(self):
        """Instance of Content View entity."""
        return ContentViewEntity(self.browser)

    @cached_property
    def hostcollection(self):
        """Instance of Host Collection entity."""
        return HostCollectionEntity(self.browser)

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
    def subnet(self):
        """Instance of Subnet entity."""
        return SubnetEntity(self.browser)

    @cached_property
    def syncplan(self):
        """Instance of Sync Plan entity."""
        return SyncPlanEntity(self.browser)
