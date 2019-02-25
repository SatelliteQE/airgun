from airgun.helpers.base import BaseEntityHelper


class HostHelper(BaseEntityHelper):

    def read_create_view(self, values, read_widget_names=None):
        """Goto create create host view, fill the view with supplied values, and return widgets
        read values, will read only read_widget_names if supplied otherwise read view widgets.
        """
        return self.read_filled_view('New', values=values, read_widget_names=read_widget_names)
