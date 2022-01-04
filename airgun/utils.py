import functools
import time


def merge_dict(values, new_values):
    """Update dict values with new values from new_values dict

    Merge example:

        a = {'a': {'c': {'k': 2, 'x': {1: 0}}}}
        b = {'a': {'c': {'z': 5, 'y': 40, 'x': {2: 1}}}, 'b': {'a': 1, 'l': 2}}
        update_dict(a, b)
        # a updated and equal:
        # {'a': {'c': {'k': 2, 'x': {1: 0, 2: 1}, 'z': 5, 'y': 40}}, 'b': {'a': 1, 'l': 2}}
    """
    for key in new_values:
        if key in values and isinstance(values[key], dict) and isinstance(new_values[key], dict):
            merge_dict(values[key], new_values[key])
        else:
            values[key] = new_values[key]


def normalize_dict_values(values):
    """Transform a widget path:value dict to a regular View read values format.

    This function transform a dictionary from:
       {'a.b': 1, 'a.z': 10, 'a.c.k': 2, 'a.c.z': 5, 'x.y': 3, 'c': 4}
    to:
       {'a': {'b': 1, 'z': 10, 'c': {'k': 2, 'z': 5}}, 'x': {'y': 3}, 'c': 4}
    """
    new_values = {}
    for key, value in values.items():
        keys = key.split('.')
        new_key = keys.pop(0)
        if keys:
            new_key_value = normalize_dict_values({'.'.join(keys): value})
        else:
            new_key_value = value
        if (
            new_key in new_values
            and isinstance(new_values[new_key], dict)
            and isinstance(new_key_value, dict)
        ):
            # merge in place the new_values with new_key_value
            merge_dict(new_values[new_key], new_key_value)
        else:
            new_values[new_key] = new_key_value
    return new_values


def get_widget_by_name(widget_root, widget_name):
    """Return a widget by it's name from widget_root, where widget can be a sub widget.

    :param widget_root: The root Widget instance from where to begin resolving widget_name.
    :param widget_name: a string representation of the widget instance to find.

    Example:
         widget_name = 'details'
         or
         widget_name = 'details.subscription_status'
         or
         widget_name = 'details.subscriptions.resources'
    """
    widget = widget_root
    for sub_widget_name in widget_name.split('.'):
        name = sub_widget_name
        if name not in widget.widget_names:
            name = name.replace(' ', '_')
            name = name.lower()
            if name not in widget.widget_names:
                raise AttributeError(
                    f'Object <{widget.__class__}> has no widget name "{sub_widget_name}"'
                )
        widget = getattr(widget, name)
    return widget


def retry_navigation(method):
    """Decorator to invoke method one or more times, if TimedOutError is raised."""

    @functools.wraps(method)
    def retry_wrapper(*args, **kwargs):
        attempts = 3
        for i in range(attempts):
            try:
                return method(*args, **kwargs)
            except (Exception):
                if i < attempts - 1:
                    args[0].view.parent.browser.refresh()
                    time.sleep(0.5)
                else:
                    raise

    return retry_wrapper
