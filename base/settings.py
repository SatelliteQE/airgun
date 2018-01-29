import configparser
import os

from logging import basicConfig


SETTINGS_FILE_NAME = 'settings.ini'


def get_project_root():
    """Return the path to the project root directory.

    :return: A directory path.
    :rtype: str
    """
    return os.path.realpath(os.path.join(
        os.path.dirname(__file__),
        os.pardir,
    ))


class SatelliteSettings(object):

    def __init__(self):
        self.hostname = None
        self.username = None
        self.password = None


class SeleniumSettings(object):

    def __init__(self):
        self.browser = None
        self.webdriver = None
        self.webdriver_binary = None
        self.screenshots_path = None
        self.log_driver_commands = None


class Settings(object):

    def __init__(self):
        self.configured = False
        self.satellite = SatelliteSettings()
        self.selenium = SeleniumSettings()

    def configure(self, settings=None):
        if settings is None:
            settings_path = os.path.join(
                get_project_root(), SETTINGS_FILE_NAME)
            settings = configparser.ConfigParser()
            settings.read(settings_path)

        for section in settings.sections():
            for key, value in settings[section].items():
                setattr(getattr(self, section), key, value)

        # fixme: bugged ATM, prints twice
        basicConfig(format='%(levelname)s %(module)s:%(lineno)d: %(message)s')

        self.configured = True
