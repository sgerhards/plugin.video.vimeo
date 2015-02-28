__author__ = 'bromix'

from resources.lib import kodion


class Provider(kodion.AbstractProvider):
    def __init__(self):
        kodion.AbstractProvider.__init__(self)

        self._client = None
        self._is_logged_in = False
        pass

    def get_wizard_supported_views(self):
        return ['default', 'episodes']

    def is_logged_in(self):
        return self._is_logged_in

    def reset_client(self):
        self._client = None
        pass

    def get_client(self, context):
        # set the items per page (later)
        items_per_page = context.get_settings().get_items_per_page()

        access_manager = context.get_access_manager()
        access_token = access_manager.get_access_token()
        if access_manager.is_new_login_credential() or not access_token or access_manager.is_access_token_expired():
            # reset access_token
            access_manager.update_access_token('')
            # we clear the cache, so none cached data of an old account will be displayed.
            context.get_function_cache().clear()
            # reset the client
            self._client = None
            pass

        if not self._client:
            language = context.get_settings().get_string('youtube.language', 'en-US')

            # remove the old login.
            if access_manager.has_login_credentials():
                access_manager.remove_login_credentials()
                pass

            if access_manager.has_login_credentials() or access_manager.has_refresh_token():
                username, password = access_manager.get_login_credentials()
                access_token = access_manager.get_access_token()
                refresh_token = access_manager.get_refresh_token()

                # create a new access_token
                """
                if not access_token and username and password:
                    access_token, expires = YouTube(language=language).authenticate(username, password)
                    access_manager.update_access_token(access_token, expires)
                    pass
                """
                if not access_token and refresh_token:
                    access_token, expires = YouTube(language=language).refresh_token(refresh_token)
                    access_manager.update_access_token(access_token, expires)
                    pass

                self._is_logged_in = access_token != ''
                self._client = YouTube(items_per_page=items_per_page, access_token=access_token,
                                       language=language)
                self._client.set_log_error(context.log_error)
            else:
                self._client = YouTube(items_per_page=items_per_page, language=language)
                self._client.set_log_error(context.log_error)
                pass
            pass

        return self._client

    def get_alternative_fanart(self, context):
        return self.get_fanart(context)

    def get_fanart(self, context):
        return context.create_resource_path('media', 'fanart.jpg')

    def on_root(self, context, re_match):
        result = []
        return result

    pass