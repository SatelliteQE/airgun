"""Exceptions raised by airgun"""


class ReadOnlyWidgetError(Exception):
    """Raised mainly when trying to fill a read only widget"""


class DisabledWidgetError(Exception):
    """Raised when a widget is disabled, and not usable for some contexts scenarios"""


class DestinationNotReachedError(Exception):
    """Raised when navigation destination view was not reached (not dispayed)."""
