from airgun import settings


pytest_plugins = ["airgun.fixtures"]


def pytest_collection_modifyitems():
    """called after collection has been performed, may filter or re-order
    the items in-place.
    """
    if not settings.configured:
        settings.configure()
