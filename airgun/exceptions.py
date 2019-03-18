"""Exceptions raised by airgun"""


class ReadOnlyWidgetError(Exception):
    """Raised mainly when trying to fill a read only widget"""


class DestinationNotReachedError(Exception):
    """Raised when navigation destination view was not reached (not dispayed)."""
