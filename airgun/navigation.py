"""AirGun's implementation of base navigation and navigate steps."""

from cached_property import cached_property
import navmazing
from navmazing import NavigationTriesExceeded
from selenium.common.exceptions import NoSuchElementException
from wait_for import TimedOutError, wait_for


class NavigateStep(navmazing.NavigateStep):
    """AirGun's version of :class:`navmazing.NavigateStep` with custom
    implementations of `navmazing.NavigateStep.am_i_here` and `navmazing.NavigateStep.go`
    and ability to work with views.
    """

    VIEW = None

    def __init__(self, obj, navigate_obj, logger=None):
        """Adding shortcut for navigate object to make easier calls to its
        navigate method
        """
        super().__init__(obj, navigate_obj, logger=logger)
        self.navigate_to = self.navigate_obj.navigate

    @cached_property
    def view(self):
        """Cached property which returns instance of view, which was defined
        for current navigate step by ``VIEW`` class attribute.
        """
        if self.VIEW is None:
            raise AttributeError(f'{type(self).__name__} does not have VIEW specified')
        return self.create_view(self.VIEW, additional_context={'entity': self.obj})

    def create_view(self, view_class, additional_context=None):
        """Method which creates an instance of view, defined by ``view_class``.

        Created instance will have references to ``entity``,
        :class:`airgun.browser.AirgunBrowser` and
        :class:`airgun.session.Session` set as instance attributes
        ``self.context['entity']``, ``self.browser`` and ``self.extra.session``
        correspondingly.

        :param widgetastic.widget.View view_class: class of view to create
        :param dict optional additional_context: any additional context you
            want to include. ``entity`` is set to current navigate step entity
            by default
        :return: instance of view
        :rtype: widgetastic.widget.View
        """
        if additional_context is None:
            additional_context = {}
        if not additional_context.get('entity'):
            additional_context['entity'] = self.obj
        return view_class(self.navigate_obj.browser, additional_context=additional_context)

    def am_i_here(self, *args, **kwargs):
        """Describes if the navigation is already at the requested destination.

        By default, airgun relies on view's ``is_displayed`` property to
        determine whether navigation succeeded. If positional argument
        ``entity_name`` was passed and view has ``BreadCrumb`` widget, it will
        also ensure second location in breadcrumb is provided entity name.

        This method may be overridden on specific entity's NavigateStep level
        for more complex logic if needed.

        :return: whether navigator is at requested destination or not.
        :rtype: bool
        """
        entity_name = kwargs.get('entity_name')
        try:
            if entity_name and hasattr(self.view, 'breadcrumb'):
                return self.view.is_displayed and self.view.breadcrumb.locations[1] in (
                    entity_name,
                    f'Edit {entity_name}',
                )
            return self.view.is_displayed
        except (AttributeError, NoSuchElementException):
            return False

    def go(self, _tries=None, wait_for_am_i_here=True, wait_timeout=10, *args, **kwargs):
        """Navigate with built-in retry and post-navigation validation.

        :param _tries: number of navigation attempts (default: 3)
        :param wait_for_am_i_here: whether to validate navigation succeeded by
            waiting for am_i_here to return True (default: True)
        :param wait_timeout: seconds to wait for validation (default: 10)
        :return: view instance if class attribute ``VIEW`` is set or ``None``
            otherwise
        """
        __tracebackhide__ = True
        max_tries = _tries if _tries is not None else getattr(self, '_default_tries', 3)

        for attempt in range(0, max_tries + 1):
            try:
                # Call parent class navigation logic
                super().go(*args, _tries=0, **kwargs)

                # Validate navigation succeeded
                if wait_for_am_i_here and self.VIEW is not None:
                    wait_for(
                        self.am_i_here,
                        func_args=args,
                        func_kwargs=kwargs,
                        num_sec=wait_timeout,
                        message=f'Waiting for am_i_here of {type(self).__name__}',
                        handle_exception=True,
                        raise_original=True,
                    )

                return self.view if self.VIEW is not None else None

            except (TimedOutError, NoSuchElementException) as e:
                if attempt < max_tries:
                    if self.logger:
                        self.logger.info(
                            f'Navigation attempt {attempt + 1} failed: {e}, retrying...'
                        )
                    continue
                else:
                    raise

        raise NavigationTriesExceeded(
            f'{type(self.obj).__name__}, "{self._name}" - failed after {max_tries} attempts'
        )


class Navigate(navmazing.Navigate):
    """Wrapper around :class:`navmazing.Navigate` which adds airgun browser as
    class attribute.

    For more information about :class:`Navigate` please refer to
    `navmazing docs <https://github.com/RedHatQE/navmazing>`_.
    """

    def __init__(self, browser=None):
        """Store airgun browser instance to be able to perform navigation
        steps.

        :param airgun.browser.AirgunBrowser browser: airgun browser instance to
            perform navigation with
        """
        super().__init__()
        self.browser = browser


# Navigator instance to be used in other modules. Please note that you should
# use it only for registering navigation steps, not for actual navigation. For
# navigation use :attr:`airgun.Session.navigate_to` instead.
navigator = Navigate()
