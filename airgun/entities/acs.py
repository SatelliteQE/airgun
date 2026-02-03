from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.acs import (
    AddAlternateContentSourceModal,
    AlternateContentSourcesView,
    EditCapsulesModal,
    EditCredentialsModal,
    EditDetailsModal,
    EditProductsModal,
    EditUrlAndSubpathsModal,
    RowDrawer,
)


class AcsEntity(BaseEntity):
    def wait_for_content_table(self, view):
        wait_for(lambda: view.acs_drawer.content_table.is_displayed, timeout=10, delay=1)

    def get_row_drawer_content(self, row_id=None, acs_name=None):
        """
        Function that returns a dictionary with one ACS detail

        Args:
            row_id (int): Row ID of ACS item in ACS table
            acs_name (str): ACS name to get info of

        Raises:
            ValueError: If row_id and acs_name are not specified or both specified
            ValueError: If no ACS is found
            ValueError: If given ACS name does not exist
        """

        if (row_id is None and acs_name is None) or (row_id is not None and acs_name is not None):
            raise ValueError('Either row_id or acs_name must be specified!')

        view = self.navigate_to(self, 'ACS')
        if not view.acs_drawer.content_table.is_displayed:
            raise ValueError('No ACS found!')

        if row_id is not None:
            view.acs_drawer.content_table[row_id][1].widget.click()
        elif acs_name is not None:
            view.acs_drawer.search_bar.fill(f'name = {acs_name}')

            if not view.acs_drawer.content_table.is_displayed:
                raise ValueError(f'ACS {acs_name} not found!')
            # Open ACS details side panel
            view.acs_drawer.content_table[0][1].widget.click()

        result = RowDrawer(self.browser).read()
        result['details']['last_refresh'] = RowDrawer(self.browser).last_refresh.text
        self.close_details_side_panel()
        return result

    def get_all_acs_info(self):
        """
        Function that returns list of dictionaries where each dictionary
        is one ACS represented on one row of the ACS table
        """

        view = self.navigate_to(self, 'ACS')
        if view.acs_drawer.clear_search_btn.is_displayed:
            view.acs_drawer.clear_search_btn.click()
        wait_for(lambda: view.acs_drawer.content_table.is_displayed, timeout=10, delay=1)
        acs_table = view.acs_drawer.content_table.read()
        for i, row in enumerate(acs_table):
            row['details'] = self.get_row_drawer_content(row_id=i)
        return acs_table

    def item_action(self, acs_name=None, action=None):
        """
        Function that performs action[Refresh, Delete] on ACS item(s)

        Args:
            acs_name (str or list): ACS name or list of ACS names
            action (str): Action to be performed on ACS item(s) [Refresh, Delete]

        Raises:
            ValueError: If acs_name or action is not specified
            ValueError: If acs_name is empty list
            ValueError: If ACS is not found
            ValueError: If error message is displayed
        """

        if acs_name is None or action is None:
            raise ValueError('Either acs_name and action must be specified!')
        if isinstance(acs_name, list) and not acs_name:
            raise ValueError('acs_name must not be empty list!')

        view = self.navigate_to(self, 'ACS')
        # Convert string to list for further use
        acs_name = [acs_name] if isinstance(acs_name, str) else acs_name

        for acs in acs_name:
            view.acs_drawer.search_bar.fill(f'name = {acs}')
            if not view.acs_drawer.content_table.is_displayed:
                raise ValueError(f'ACS {acs} not found!')
            # Check the checkbox of ACS item
            view.acs_drawer.content_table[0][0].widget.click()

        # Wait for ACS table to be refreshed
        wait_for(lambda: view.acs_drawer.content_table.is_displayed, timeout=10, delay=1)

        view.acs_drawer.kebab_menu.item_select(action)
        if view.error_message.is_displayed:
            raise ValueError(f'Error while taking an action on ACS: {view.error_message.read()}')
        if action == 'Refresh':
            view.acs_drawer.clear_search_btn.click()

        self.browser.plugin.do_refresh()
        wait_for(lambda: view.acs_drawer.content_table.is_displayed, timeout=10, delay=1)

    def refresh_acs(self, acs_name):
        """Function that refreshes ACS item(s)"""
        self.item_action(acs_name, 'Refresh')

    def delete_acs(self, acs_name):
        """Function that deletes ACS item(s)"""
        self.item_action(acs_name, 'Delete')

    def all_items_action(self, action):
        """
        Function that performs action[Refresh, Delete] on all ACS items

        Args:
            action (str): Action to be performed on all ACS items [Refresh, Delete]

        Raises:
            ValueError: If no ACS is found
            ValueError: If error message is displayed
        """

        view = self.navigate_to(self, 'ACS')
        wait_for(lambda: view.acs_drawer.content_table.is_displayed, timeout=10, delay=1)
        if not view.acs_drawer.content_table.is_displayed:
            raise ValueError('No ACS found!')

        # Wait for ACS table to be refreshed
        self.wait_for_content_table(view)
        view.acs_drawer.select_all.click()
        view.acs_drawer.kebab_menu.item_select(action)
        if view.error_message.is_displayed:
            raise ValueError(
                f'Error while taking an action on all ACS: {view.error_message.read()}'
            )

        self.browser.plugin.do_refresh()
        wait_for(lambda: view.title.is_displayed, timeout=10, delay=1)

    def refresh_all_acs(self):
        """Function that refreshes all ACS items"""
        self.all_items_action('Refresh')

    def delete_all_acs(self):
        """Function that deletes all ACS items"""
        self.all_items_action('Delete')

    def edit_helper(self, acs_name_to_edit):
        """
        Helper function that navigates to ACS item and loads side panel view

        Args:
            acs_name_to_edit (str): ACS name to edit

        Raises:
            ValueError: If acs_name_to_edit cannot be found
        """

        view = self.navigate_to(self, 'ACS')

        # Check if acs we want to edit exists
        view.acs_drawer.search_bar.fill(f'name = {acs_name_to_edit}')

        if not view.acs_drawer.content_table.is_displayed:
            raise ValueError(f'ACS {acs_name_to_edit} not found!')
        # Click on ACS name in ACS table
        view.acs_drawer.content_table[0][1].widget.click()
        # Load side panel view
        view = RowDrawer(self.browser)
        wait_for(lambda: view.details.title.is_displayed, timeout=10, delay=1)
        return view

    def close_details_side_panel(self):
        """Function that closes side panel view"""

        view = AlternateContentSourcesView(self.browser)

        view.acs_drawer.content_table[0][1].widget.click()

    def edit_acs_details(
        self, acs_name_to_edit=None, new_acs_name=None, new_description=None, check_parameters=True
    ):
        """
        Function that edits ACS items details

        Args:
            acs_name_to_edit (str): ACS name to be edited
            new_acs_name (str): New ACS name
            new_description (str): Description to be set for ACS item
            check_parameters (bool): Whether to check function parameters

        Raises:
            ValueError: At least acs_name_to_edit and one of new_acs_name or new_description
                        must be specified!
            ValueError: If Error alert is displayed after editing ACS item
        """

        if (
            (acs_name_to_edit is None)
            and ((new_acs_name is None) or (new_description is None))
            and check_parameters
        ):
            raise ValueError(
                'At least acs_name_to_edit and one of new_acs_name or new_description '
                'must be specified!'
            )

        view = self.edit_helper(acs_name_to_edit)
        view.details.edit_details.click()
        # Load EditDetailsModal view
        view = EditDetailsModal(self.browser)
        if new_acs_name is not None:
            view.name.fill(new_acs_name)
        if new_description is not None:
            view.description.fill(new_description)
        view.edit_button.click()
        # Wait for the possible error to pop up

        if view.error_message.is_displayed:
            raise ValueError(f'Error while editing: {view.error_message.read()}')
        self.close_details_side_panel()

    def dual_list_selector_edit_helper(
        self,
        view=None,
        add_all=False,
        remove_all=False,
        options_to_add=None,
        options_to_remove=None,
    ):
        """
        Function that provides action over dual list selector
        like adding one or selection of items from left or right list,
        adding or removing all items from left or right list
        and submitting the changes.

        It also checks if entered parameters are valid.

        Args:
            view: View to be used for the action
            add_all (bool): Whether to add all available options
            remove_all (bool): Whether to remove all available options
            options_to_add (str or list): List of options to add
            options_to_remove (str or list): List of options to remove

        Raises:
            ValueError: When given option is not available for addition
            ValueError: When given option is not available for removal
            ValueError: If add_all is True but add_all button is disabled
            ValueError: If remove_all is True but remove_all button is disabled
        """

        # Manage the options
        if options_to_add is not None:
            for option in options_to_add:
                view.available_options_search.fill(option)
                # Check if option is available
                x = view.available_options_list.read()
                if (not option) or (option not in x):
                    raise ValueError(f'Option {option} not available for addition!')
                view.available_options_list.fill(option)
            view.add_selected.click()

        if options_to_remove is not None:
            for option in options_to_remove:
                view.chosen_options_search.fill(option)
                # Check if option is available to be removed
                x = view.chosen_options_list.read()
                if (not option) or (option not in x):
                    raise ValueError(f'Option {option} not available for removing!')
                view.chosen_options_list.fill(option)
            view.remove_selected.click()

        if add_all:
            if view.add_all.disabled:
                raise ValueError('Add all button is disabled, cannot add all options!')
            view.add_all.click()
        if remove_all:
            remove_all_flag = view.remove_all.disabled
            if remove_all_flag:
                raise ValueError('Remove all button is disabled, cannot remove all options!')
            view.remove_all.click()

        view.edit_button.click()

    def edit_capsules(
        self,
        acs_name_to_edit=None,
        use_http_proxies=False,
        add_all=False,
        remove_all=False,
        options_to_add=None,
        options_to_remove=None,
        check_parameters=True,
    ):
        """
        Function that edits ACS capsules.

        Args:
            acs_name_to_edit (str): ACS name to be edited
            use_http_proxies (bool): Whether to use HTTP proxies
            add_all (bool): Whether to add all available options
            remove_all (bool): Whether to remove all available options
            options_to_add (str or list): List of options to add
            options_to_remove (str or list): List of options to remove
            check_parameters (bool): Whether to check function parameters

        Raises:
            ValueError: If add_all and remove_all are True at the same time
            ValueError: If add_all or remove_all are True at the same time
                        with options_to_add or options_to_remove
        """
        if check_parameters:
            if add_all and remove_all:
                raise ValueError('add_all and remove_all cannot be True at the same time!')
            if (add_all or remove_all) and (
                options_to_add is not None or options_to_remove is not None
            ):
                raise ValueError(
                    'add_all or remove_all cannot be True at the same time with '
                    'options_to_add or options_to_remove!'
                )

        # Check options parameters and cast them to list
        if options_to_add is not None and isinstance(options_to_add, str):
            options_to_add = [options_to_add]
        if options_to_remove is not None and isinstance(options_to_remove, str):
            options_to_remove = [options_to_remove]

        view = self.edit_helper(acs_name_to_edit)
        # Close side panel view
        view.capsules.edit_capsules.click()
        view = EditCapsulesModal(self.browser)
        wait_for(lambda: view.available_options_search.is_displayed, timeout=10, delay=1)
        # Toggle Use HTTP proxies
        if use_http_proxies is False and view.use_http_proxies.selected:
            view.use_http_proxies.click()
        if use_http_proxies is True and not view.use_http_proxies.selected:
            view.use_http_proxies.click()

        # Call helper function that handles adding/removing
        # options from dual list selector abd saves changes
        self.dual_list_selector_edit_helper(
            view, add_all, remove_all, options_to_add, options_to_remove
        )
        self.close_details_side_panel()

    def edit_url_subpaths(
        self, acs_name_to_edit=None, new_url=None, new_subpaths=None, check_parameters=True
    ):
        """
        Function that edits ACS url and subpaths

        Args:
            acs_name_to_edit (str): ACS name to be edited
            new_url (str): New ACS url
            new_subpaths (str or list): Subpaths to be set for ACS item
            check_parameters (bool): Whether to check function parameters

        Raises:
            ValueError: At least acs_name_to_edit and one of new_url
                        or new_subpaths must be specified!
            ValueError: If Error alert is displayed while editing ACS item's url or subpaths
        """
        if check_parameters:
            if (acs_name_to_edit is None) and ((new_url is None) or (new_subpaths is None)):
                raise ValueError(
                    'At least acs_name_to_edit and one of new_url or '
                    'new_subpaths must be specified!'
                )

        view = self.edit_helper(acs_name_to_edit)
        view.url_and_subpaths.edit_url_and_subpaths.click()
        # Load EditUrlAndSubpathsModal view
        view = EditUrlAndSubpathsModal(self.browser)
        new_subpaths = new_subpaths if isinstance(new_subpaths, list) else [new_subpaths]
        # if there is more than one element in new_subpaths,
        # join them to one string separated by comma as required by the satellite
        new_subpaths = ','.join(new_subpaths) if len(new_subpaths) > 1 else new_subpaths[0]
        if new_url is not None:
            view.base_url.fill(new_url)
            if view.url_err.is_displayed:
                raise ValueError(f'Error while editing url: {view.url_err.read()}')
        if new_subpaths is not None:
            view.subpaths.fill(new_subpaths)
            if view.paths_err.is_displayed:
                raise ValueError(f'Error while editing subpaths: {view.paths_err.read()}')

        # Save changes
        view.edit_button.click()
        self.close_details_side_panel()

    def edit_credentials(
        self,
        acs_name_to_edit=None,
        verify_ssl=False,
        ca_cert=None,
        manual_auth=False,
        username=None,
        password=None,
        content_credentials_auth=False,
        ssl_client_cert=None,
        ssl_client_key=None,
        none_auth=False,
        check_parameters=True,
    ):
        """
        Function that edits ACS credentials.
        User needs to choose only one of the authentication methods
        [manual_auth, content_credentials_auth, none_auth].

        Args:
            acs_name_to_edit (str): ACS name to be edited
            verify_ssl (bool): Whether to verify SSL
            ca_cert (str): CA certificate to choose
            manual_auth (bool): Whether to use manual authentication
            username (str): Username to be set
            password (str): Password to be set
            content_credentials_auth (bool): Whether to use content credentials authentication
            ssl_client_cert (str): SSL client certificate to choose
            ssl_client_key (str): SSL client key to choose
            none_auth (bool): Whether to use no authentication
            check_parameters (bool): Whether to check function parameters

        Raises:
            ValueError: At least acs_name_to_edit and one of manual_auth,
                        content_credentials_auth, none_auth must be specified!
            ValueError: At least one of username and password
                        must be specified when using manual authentication
            ValueError: At least one of ssl_client_cert and ssl_client_key
                        must be specified when using credentials
        """

        if (
            check_parameters
            and acs_name_to_edit is None
            and (sum([manual_auth, content_credentials_auth, none_auth] != 1))
        ):
            raise ValueError(
                'At least acs_name_to_edit and one of '
                'manual_auth, content_credentials_auth, none_auth must be specified!'
            )

        view = self.edit_helper(acs_name_to_edit)
        view.credentials.edit_credentials.click()
        # Load EditCredentialsModal view
        view = EditCredentialsModal(self.browser)
        wait_for(lambda: view.verify_ssl_toggle.is_displayed, timeout=10, delay=1)

        # Toggle verify_ssl
        if verify_ssl is False and view.verify_ssl_toggle.selected:
            view.verify_ssl_toggle.click()
        if verify_ssl is True and not view.verify_ssl_toggle.selected:
            view.verify_ssl_toggle.click()

        # Select CA certificate
        if ca_cert is not None and view.verify_ssl_toggle.selected:
            view.select_ca_cert.fill(ca_cert)

        # Select manual authentication method
        if manual_auth:
            if (username is None) and (password is None) and check_parameters:
                raise ValueError(
                    'At least one of username and password must be specified '
                    'when using manual authentication!'
                )

            view.manual_auth_radio_btn.fill(True)
            if username is not None:
                view.username.fill(username)
            if password is not None:
                view.password.fill(password)

        # Select content credentials authentication method
        if content_credentials_auth:
            if (ssl_client_cert is None) and (ssl_client_key is None) and check_parameters:
                raise ValueError(
                    'At least one of ssl_client_cert and ssl_client_key '
                    'must be specified when using content credentials authentication!'
                )

            view.content_credentials_radio_btn.fill(True)
            if ssl_client_cert is not None:
                view.ssl_client_cert.fill(ssl_client_cert)
            if ssl_client_key is not None:
                view.ssl_client_key.fill(ssl_client_key)

        # Select no authentication method
        if none_auth and not view.none_auth_toggle.selected:
            view.none_auth_toggle.click()

        # Save changes
        view.edit_button.click()
        self.close_details_side_panel()

    def edit_products(
        self,
        acs_name_to_edit=None,
        add_all=False,
        remove_all=False,
        products_to_add=None,
        products_to_remove=None,
        check_parameters=True,
    ):
        """
        Function that edits ACS products.

        Args:
            acs_name_to_edit (str): ACS name to be edited
            add_all (bool): Whether to add all available options
            remove_all (bool): Whether to remove all available options
            products_to_add (str or list): List of products to add
            products_to_remove (str or list): List of products to remove
            check_parameters (bool): Whether to check function parameters

        Raises:
            ValueError: If add_all and remove_all are True at the same time
            ValueError: If add_all or remove_all are True at the same time
                        with options_to_add or options_to_remove
        """

        if check_parameters:
            if add_all and remove_all:
                raise ValueError('add_all and remove_all cannot be True at the same time!')
            if (add_all or remove_all) and (
                products_to_add is not None or products_to_remove is not None
            ):
                raise ValueError(
                    'add_all or remove_all cannot be True at the same time with '
                    'options_to_add or options_to_remove!'
                )

        # Check options parameters and cast them to list
        if products_to_add is not None and isinstance(products_to_add, str):
            products_to_add = [products_to_add]
        if products_to_remove is not None and isinstance(products_to_remove, str):
            products_to_remove = [products_to_remove]

        view = self.edit_helper(acs_name_to_edit)
        view.products.edit_products.click()
        view = EditProductsModal(self.browser)
        wait_for(lambda: view.available_options_search.is_displayed, timeout=10, delay=1)
        # Call helper function that handles adding/removing options
        # from dual list selector and saves changes
        self.dual_list_selector_edit_helper(
            view, add_all, remove_all, products_to_add, products_to_remove
        )
        self.close_details_side_panel()

    def create_new_acs(  # noqa: C901 - function is too complex
        self,
        custom_type=False,
        simplified_type=False,
        rhui_type=False,
        content_type=None,
        name=None,
        description=None,
        add_all_capsules=False,
        capsules_to_add=None,
        use_http_proxies=False,
        add_all_products=False,
        products_to_add=None,
        base_url=None,
        subpaths=None,
        verify_ssl=False,
        ca_cert=None,
        manual_auth=False,
        username=None,
        password=None,
        content_credentials_auth=False,
        ssl_client_cert=None,
        ssl_client_key=None,
        none_auth=False,
        check_parameters=True,
    ):
        """
        Function that creates new ACS according to the given parameters.

        Args:
            custom_type (bool): Whether to create custom type ACS
            simplified_type (bool): Whether to create simplified type ACS
            rhui_type (bool): Whether to create RHUI type ACS
            content_type (str): Content type to be selected ['yum', 'file']
            name (str): Name of ACS to be created
            description (str): Description of ACS to be created
            add_all_capsules (bool): Whether to add all capsules
            capsules_to_add (str or list): List of capsules to add
            use_http_proxies (bool): Whether to use https proxies
            add_all_products (bool): Whether to add all products
            products_to_add (str or list): List of products to add
            base_url (str): Base URL of ACS to be created
            subpaths (str or list): List(multiple paths) ['path1/', 'foo/bar']
                                    or
                                    String(only one path) 'path1/'
                                    of subpaths to be added.
                                    !!! Each subpath entry must end with '/' !!!
            verify_ssl (bool): Whether to verify SSL
            ca_cert (str): CA certificate to be selected
            manual_auth (bool): Whether to use manual authentication
            username (str): Username to be used for manual authentication
            password (str): Password to be used for manual authentication
            content_credentials_auth (bool): Whether to use content credentials authentication
            ssl_client_cert (str): SSL client certificate to be used for content
                                    credentials authentication
            ssl_client_key (str): SSL client key to be used for content credentials authentication
            none_auth (bool): Whether to use no authentication
            check_parameters (bool): Whether to check function parameters

        Raises:
            ValueError: If more than one type is selected
            ValueError: If more than one credential type is selected
            ValueError: If content_type is specified when rhui_type is True
            ValueError: If name is None
            ValueError: If content_type is not specified when
                        custom_type or simplified_type is True
            ValueError: If capsules_to_add is none when add_all_capsules is False
            ValueError: If products_to_add is none when add_all_products is False
            ValueError: If base_url is None and custom_type or rhui_type is True
            ValueError: If verify_ssl is False and ca_cert is not None
            ValueError: If manual_auth is True and username and password is None
            ValueError: If rhui_type is True and manual_auth is True
            ValueError: If given capsule is not available for addition
            ValueError: If you are trying to create ACS with already taken name
            ValueError: If given product is not available for addition
            ValueError: If base url is not valid
            ValueError: If subpaths are not valid
            ValueError: If there is some general error after adding ACS
        """
        if check_parameters:
            # CHECK THE PARAMETERS
            if sum([custom_type, simplified_type, rhui_type]) != 1:
                raise ValueError('Only one type can be selected!')

            if custom_type or rhui_type:
                if sum([manual_auth, content_credentials_auth, none_auth]) != 1:
                    raise ValueError('Only one credential type can be selected!')

            if rhui_type and content_type is not None:
                raise ValueError('content_type cannot be specified when rhui_type is True!')

            if name is None:
                raise ValueError('name cannot be None!')

            if (custom_type or simplified_type) and content_type is None:
                raise ValueError(
                    'content_type cannot be None when custom_type or simplified_type is True!'
                )

            if add_all_capsules is False and capsules_to_add is None:
                raise ValueError('capsules_to_add cannot be None when add_all_capsules is False!')

            if simplified_type and (add_all_products is False and products_to_add is None):
                raise ValueError(
                    'While simplified mode is selected '
                    'products_to_add cannot be None when add_all_products is False!'
                )

            if (custom_type is True or rhui_type is True) and base_url is None:
                raise ValueError('base_url cannot be None when custom_type or rhui_type is True!')

            if verify_ssl is False and ca_cert is not None:
                raise ValueError('ca_cert must be None when verify_ssl is False!')

            if manual_auth is True and (username is None or password is None):
                raise ValueError('username and password cannot be None when manual_auth is True!')

            if rhui_type is True and manual_auth is True:
                raise ValueError('manual_auth cannot be True when rhui_type is True!')

        view = self.navigate_to(self, 'ACS')
        # If there are some ACS already created
        if view.acs_drawer.content_table.is_displayed:
            # Check if we are not creating ACS with the name that already exists
            view.acs_drawer.search_bar.fill(f'name = {name}')
            if view.acs_drawer.content_table.is_displayed:
                raise ValueError(f'ACS with {name} already exists!')
            else:
                view.acs_drawer.clear_search.click()

        wait_for(lambda: view.acs_drawer.add_source.is_displayed, timeout=10, delay=1)
        view.acs_drawer.add_source.click()
        # Load wizard modal for adding new ACS
        view = AddAlternateContentSourceModal(self.browser)

        wait_for(lambda: view.title.is_displayed, timeout=10, delay=1)

        # Select ACS type
        if custom_type:
            view.select_source_type.custom_option.click()
            view.select_source_type.content_type_select.fill(content_type.capitalize())
        elif simplified_type:
            view.select_source_type.simplified_option.click()
            view.select_source_type.content_type_select.fill(content_type.capitalize())
        elif rhui_type:
            view.select_source_type.rhui_option.click()

        # Fill name and description
        view.name_source
        view.fill({'name_source.name': name, 'name_source.description': description})

        # Select capsules
        if add_all_capsules:
            view.select_capsule.add_all.click()
        if capsules_to_add is not None:
            # If provided argument is string, convert it to list
            if isinstance(capsules_to_add, str):
                capsules_to_add = [capsules_to_add]
            for capsule in capsules_to_add:
                view.select_capsule.available_options_search.fill(capsule)
                # Check if capsule is available
                x = view.select_capsule.available_options_list.read()
                if (not capsule) or (capsule not in x):
                    raise ValueError(f'Capsule {capsule} not available for adition!')
                view.select_capsule.available_options_list.fill(capsule)
            view.select_capsule.add_selected.click()

        if use_http_proxies:
            view.select_capsule.use_http_proxies.fill(True)

        # Select products
        if simplified_type:
            if add_all_products:
                view.select_products.add_all.click()
            if products_to_add is not None:
                # If provided argument is string, convert it to list
                if isinstance(products_to_add, str):
                    products_to_add = [products_to_add]
                for product in products_to_add:
                    view.select_products.available_options_search.fill(product)
                    # Check if product is available
                    x = view.select_products.available_options_list.read()
                    if (not product) or (product not in x):
                        raise ValueError(f'Product {product} not available for adition!')
                    view.select_products.available_options_list.fill(product)
                view.select_products.add_selected.click()

        # Fill in URLs and paths and credentials
        if custom_type or rhui_type:
            # URLs and paths
            view.url_and_paths.base_url.fill(base_url)
            if view.url_and_paths.url_err.is_displayed:
                raise ValueError(f'Error while adding url: {view.url_and_paths.url_err.read()}')
            if subpaths is not None:
                # Create string to be filled as subpaths
                if isinstance(subpaths, list):
                    subpaths = ','.join(subpaths) if len(subpaths) > 1 else subpaths[0]
                if isinstance(subpaths, str):
                    view.url_and_paths.subpaths.fill(subpaths)
                if view.url_and_paths.paths_err.is_displayed:
                    raise ValueError(
                        f'Error while editing subpaths: {view.url_and_paths.paths_err.read()}'
                    )

            # Credentials
            if verify_ssl:
                view.credentials.verify_ssl_toggle.fill(True)
                if ca_cert is not None:
                    view.credentials.select_ca_cert.fill(ca_cert)
            if manual_auth:
                view.fill(
                    {
                        'credentials.manual_auth_radio_btn': True,
                        'credentials.username': username,
                        'credentials.password': password,
                    }
                )
            elif content_credentials_auth:
                view.fill(
                    {
                        'credentials.content_credentials_radio_btn': True,
                        'credentials.ssl_client_cert': ssl_client_cert,
                        'credentials.ssl_client_key': ssl_client_key,
                    }
                )
            elif none_auth:
                view.credentials.none_auth_radio_btn.fill(True)

        # Confirm addition
        view.review_details.add_button.click()
        # Wait for modal to close
        wait_for(lambda: view.title.is_displayed is False, timeout=10, delay=1)
        # Check that there is no error message after adding new ACS
        view = AlternateContentSourcesView(self.browser)
        if view.error_message.is_displayed:
            raise ValueError(f'Error while adding ACS: {view.error_message.read()}')
        # Wait for ACS to be added to the table

        wait_for(lambda: view.acs_drawer.content_table.is_displayed, timeout=10, delay=1)
        # Close the side panel
        view = AlternateContentSourcesView(self.browser)
        view.acs_drawer.content_table[-1][1].widget.click()


@navigator.register(AcsEntity, 'ACS')
class OpenAcsPage(NavigateStep):
    """Navigate to the ACS page"""

    VIEW = AlternateContentSourcesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Alternate Content Sources')
