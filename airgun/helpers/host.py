from airgun.helpers.base import BaseEntityHelper


class HostHelper(BaseEntityHelper):

    def read_create_view(self, values, read_widget_names=None):
        """Open create host view, fill entity fields with supplied values, and then return widgets
        values. Read values from 'read_widget_names' list if provided otherwise read values from
        all view widgets.
        """
        return self.read_filled_view('New', values=values, read_widget_names=read_widget_names)

    def read_set_puppet_class_parameter_value(self, entity_name, name, value,
                                              read_widget_names=None):
        """Open update host view of entity_name, fill entity puppet smart class parameter value
        with supplied value, and then return widgets values. Read values from 'read_widget_names'
        list if provided otherwise read values from all view widgets.

        :param str entity_name: The host name for which to set the parameter value.
        :param str name: the parameter name.
        :param dict value: The parameter value
        :param list read_widget_names: [optional] The widget names to read.
        """
        view = self.entity.navigate_to(self.entity, 'Edit', entity_name=entity_name)
        view.parameters.puppet_class_parameters.row(name=name).fill({'Value': value})
        return view.read(widget_names=read_widget_names)
