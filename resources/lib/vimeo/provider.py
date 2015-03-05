from resources.lib.kodion.items import DirectoryItem, UriItem
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
            if access_manager.has_login_credentials() or access_manager.has_refresh_token():
                username, password = access_manager.get_login_credentials()
                access_token = access_manager.get_access_token()
                refresh_token = access_manager.get_refresh_token()

                # create a new access_token
                if not access_token and username and password:
                    data = Client().login(username, password)
                    access_manager.update_access_token(access_token=data.get('oauth_token'),
                                                       refresh_token=data.get('oauth_token_secret'))
                    pass

                access_token = access_manager.get_access_token()
                refresh_token = access_manager.get_refresh_token()

                if access_token and refresh_token:
                    self._client = Client(oauth_token=access_token, oauth_token_secret=refresh_token)
                else:
                    self._client = Client()
                    pass

                self._is_logged_in = access_token != ''
            else:
                self._client = Client()
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

    @kodion.RegisterProviderPath('^/my/(?P<category>(feed|likes|watch-later))/$')
    def _on_my_stuff(self, context, re_match):
        context.set_content_type(kodion.constants.content_type.EPISODES)

        result = []

        client = self.get_client(context)
        page = int(context.get_param('page', '1'))
        category = re_match.group('category')
        xml = ''
        if category == 'feed':
            xml = client.get_my_feed(page=page)
        elif category == 'likes':
            xml = client.get_my_likes(page=page)
        elif category == 'watch-later':
            xml = client.get_watch_later(page=page)
            pass

        result.extend(helper.do_xml_video_response(context, self, xml))

        return result

    @kodion.RegisterProviderPath('^/play/$')
    def _on_play(self, context, re_match):
        def _compare(item):
            vq = context.get_settings().get_video_quality()
            return vq - item['resolution']

        video_id = context.get_param('video_id')
        xml = self.get_client(context).get_video_streams(video_id=video_id)

        video_streams = helper.do_xml_to_video_stream(context, self, xml)
        video_stream = kodion.utils.find_best_fit(video_streams, _compare)

        return UriItem(video_stream['url'])

    def on_root(self, context, re_match):
        result = []

        client = self.get_client(context)

        if self._is_logged_in:
            # my feed
            my_feed_item = DirectoryItem('MY FEED', context.create_uri(['my', 'feed']))
            my_feed_item.set_fanart(self.get_fanart(context))
            result.append(my_feed_item)

            # my likes
            my_likes_item = DirectoryItem('MY LIKES', context.create_uri(['my', 'likes']))
            my_likes_item.set_fanart(self.get_fanart(context))
            result.append(my_likes_item)

            # Following
            """
            following_item = DirectoryItem('FOLLOWING', context.create_uri(['my', 'contacts']))
            following_item.set_fanart(self.get_fanart(context))
            result.append(following_item)
            """

            # Watch Later
            watch_later_item = DirectoryItem('WATCH LATER', context.create_uri(['my', 'watch-later']))
            watch_later_item.set_fanart(self.get_fanart(context))
            result.append(watch_later_item)
            pass

        # search
        search_item = kodion.items.SearchItem(context, image=context.create_resource_path('media', 'search.png'),
                                              fanart=self.get_fanart(context))
        result.append(search_item)

        return result

    pass