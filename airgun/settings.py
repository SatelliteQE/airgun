import configparser
import logging
import os

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

# todo: probably should use properties instead of class attributes
# and use setters for validation


class AirgunSettings(object):

    def __init__(self):
        self.verbosity = None


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


class Settings(object):

    def __init__(self):
        self.configured = False
        self.airgun = AirgunSettings()
        self.satellite = SatelliteSettings()
        self.selenium = SeleniumSettings()

    def _configure_logging(self):
        logging.captureWarnings(False)
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=self.airgun.verbosity
        )
        logging.getLogger('airgun').setLevel(self.airgun.verbosity)

    def _configure_thirdparty_logging(self):
        loggers = (
            'selenium.webdriver.remote.remote_connection',
            'widgetastic_null'
        )
        for logger in loggers:
            logging.getLogger(logger).setLevel(self.airgun.verbosity)

    def configure(self, settings=None):
        """Parses arg `settings` or settings file if None passed and sets class
        attributes accordingly
        """
        config = configparser.ConfigParser()
        if settings is not None:
            for section in settings:
                config.add_section(section)
                for key, value in settings[section].items():
                    config.set(section, key, str(value))
        else:
            settings_path = os.path.join(
                get_project_root(), SETTINGS_FILE_NAME)
            config.read(settings_path)

        for section in config.sections():
            for key, value in config[section].items():
                setattr(getattr(self, section), key, value)

        self._configure_logging()
        self._configure_thirdparty_logging()

        self.configured = True
