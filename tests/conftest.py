from airgun import settings
from airgun.fixtures import session  # noqa


# todo: make sure this hook is needed - for unit tests configuring may be
# redundant
def pytest_collection_modifyitems():
    """ called after collection has been performed, may filter or re-order
    the items in-place.
    """
    if not settings.configured:
        settings.configure()
