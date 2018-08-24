import importscan
from pkg_resources import iter_entry_points

from airgun.base.application.implementations.web_ui import WebUI
from airgun.base.application.implementations import AirgunImplementationContext
from airgun.base.modeling import EntityCollections


class Application(object):
    def __init__(self, hostname, path=None, scheme="https"):
        self.application = self
        self.hostname = hostname
        self.path = path
        self.scheme = scheme
        self.web_ui = ViaUI(owner=self)
        self.context = AirgunImplementationContext.from_instances([self.browser])
        self.collections = EntityCollections.for_application(self)

    @property
    def address(self):
        return "{}://{}/{}".format(self.scheme, self.hostname, self.path)

    @property
    def destinations(self):
        """Returns a dict of all valid destinations for a particular object"""
        return {
            impl.name: impl.navigator.list_destinations(self)
            for impl in self.application.context.implementations.values()
            if impl.navigator
        }


def load_application_collections():
    return {
        ep.name: ep.resolve() for ep in iter_entry_points("airgun.application_collections")
    }


from airgun import base  # noqa

importscan.scan(base)
