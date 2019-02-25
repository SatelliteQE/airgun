from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from airgun.entities.base import BaseEntity


class BaseEntityHelper:

    def __init__(self, entity):
        # type: (BaseEntity) -> None
        self._entity = entity

    @property
    def entity(self):
        return self._entity

    def read_filled_view(self, navigation_name, navigation_kwargs=None, values=None,
                         read_widget_names=None):
        # type: (str, Dict, Dict[str, Any], List[str]) -> Dict[str, Any]
        """Navigate to a form with registered name navigation_name and with kwargs
        navigation_kwargs, fill the form with values and read read_widget_names if supplied
        otherwise read all the view widgets.

        Example usage:

            # In host entity open create view/form click host.reset_puppet_environment and read
            # host.puppet_environment
            session.host.helper.read_filled_view(
                'New',
                values={'host.reset_puppet_environment': True},
                read_widget_names=['host.puppet_environment']
            )
        """
        if navigation_kwargs is None:
            navigation_kwargs = {}
        if values is None:
            values = {}
        view = self.entity.navigate_to(self.entity, name=navigation_name, **navigation_kwargs)
        view.fill(values)
        return view.read(widget_names=read_widget_names)
