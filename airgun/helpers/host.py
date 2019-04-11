from airgun.helpers.base import BaseEntityHelper


class HostHelper(BaseEntityHelper):

    def read_create_view(self, values, read_widget_names=None):
        """Open create host view, fill entity fields with supplied values, and then return widgets
        values. Read values from 'read_widget_names' list if provided otherwise read values from
        all view widgets.
        """
        return self.read_filled_view('New', values=values, read_widget_names=read_widget_names)
