from airgun.helpers.base import BaseEntityHelper


class HostHelper(BaseEntityHelper):

    def form_create_fill_read(self, values, read_widget_names=None):
        """Goto create host view, fill the view with supplied values, and return the view read
        fields values, will read only read_widget_names if supplied otherwise read the fields in
        values.
        """
        return self.form_fill_reader('New', values=values, read_widget_names=read_widget_names)
