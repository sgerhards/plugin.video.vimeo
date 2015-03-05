from resources.lib.vimeo.client import Client

__author__ = 'bromix'

from resources.lib import kodion
from resources.lib.vimeo import helper

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
                    access_token, expires = Client(oauth_token=access_token, oauth_token_secret=refresh_token)
                    access_manager.update_access_token(access_token, expires)
                    pass

                self._is_logged_in = access_token != ''
                self._client = Client(oauth_token=access_token, oauth_token_secret=refresh_token)
                #self._client.set_log_error(context.log_error)
            else:
                self._client = Client()
                #self._client.set_log_error(context.log_error)
                pass
            pass

        return self._client

    def get_alternative_fanart(self, context):
        return self.get_fanart(context)

    def get_fanart(self, context):
        return context.create_resource_path('media', 'fanart.jpg')

    def on_search(self, search_text, context, re_match):
        context.set_content_type(kodion.constants.content_type.EPISODES)

        result = []

        client = self.get_client(context)
        page = int(context.get_param('page', '1'))
        xml = client.search(query=search_text, page=page)
        result.extend(helper.do_xml_video_response(context, self, xml))

        return result

    def on_root(self, context, re_match):
        result = []

        client = self.get_client(context)

        # search
        search_item = kodion.items.SearchItem(context, image=context.create_resource_path('media', 'search.png'),
                                              fanart=self.get_fanart(context))
        result.append(search_item)

        return result

    pass