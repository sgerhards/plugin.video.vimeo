from resources.lib.kodion.items import VideoItem, NextPageItem
from resources.lib.kodion.items.directory_item import DirectoryItem

__author__ = 'bromix'

import xml.etree.ElementTree as ET


def do_xml_to_video_stream(context, provider, xml):
    result = []
    root = ET.fromstring(xml)
    video = root.find('video')
    if video is not None:
        for video_file in video.iter('file'):
            height = int(video_file.get('height'))
            url = video_file.get('url')
            mime_type = video_file.get('mime_type')

            video_info = {'url': url,
                          'resolution': height,
                          'format': mime_type}
            result.append(video_info)
            pass
        pass
    return result


def _do_next_page(result, xml_element, context, provider):
    if len(result) > 0:
        current_page = int(xml_element.get('page', '1'))
        videos_per_page = int(xml_element.get('perpage', '1'))
        total_videos = int(xml_element.get('total', '1'))
        if videos_per_page * current_page < total_videos:
            next_page_item = NextPageItem(context, current_page)
            next_page_item.set_fanart(provider.get_fanart(context))
            result.append(next_page_item)
            pass
        pass
    pass
    pass


def _do_xml_error(context, provider, root_element):
    status = root_element.get('stat')
    if status == 'fail':
        error_item = root_element.find('err')
        if error_item is not None:
            message = error_item.get('msg')
            explanation = error_item.get('expl')
            message = '%s - %s' % (message, explanation)
            context.get_ui().show_notification(message, time_milliseconds=15000)
            pass
        pass
    pass


def do_xml_video_response(context, provider, xml):
    result = []
    root = ET.fromstring(xml)
    _do_xml_error(context, provider, root)

    videos = root.find('videos')
    if videos is not None:
        for video in videos.iter('video'):
            video_id = video.get('id')
            title = video.find('title').text
            video_item = VideoItem(title, context.create_uri(['play'], {'video_id': video_id}))

            # channel name
            channel_name = ''
            owner = video.find('owner')
            if owner is not None:
                channel_name = owner.get('username', '')
                pass

            # plot
            plot = video.find('description').text
            if plot is None:
                plot = ''
                pass

            settings = context.get_settings()
            if channel_name and settings.get_bool('vimeo.view.description.show_channel_name', True):
                plot = '[UPPERCASE][B]%s[/B][/UPPERCASE][CR][CR]%s' % (channel_name, plot)
                pass
            video_item.set_plot(plot)

            # duration
            duration = int(video.find('duration', '0').text)
            if duration is not None:
                video_item.set_duration_from_seconds(duration)
                pass

            # thumbs
            thumbnails = video.find('thumbnails')
            if thumbnails is not None:
                for thumbnail in video.iter('thumbnail'):
                    height = int(thumbnail.get('height', '0'))
                    if height >= 360:
                        video_item.set_image(thumbnail.text)
                        break
                    pass
                pass

            video_item.set_fanart(provider.get_fanart(context))

            result.append(video_item)
            pass

        _do_next_page(result, videos, context, provider)
    return result


def do_xml_contacts_response(context, provider, xml):
    result = []
    root = ET.fromstring(xml)
    _do_xml_error(context, provider, root)

    contacts = root.find('contacts')
    if contacts is not None:
        for contact in contacts.iter('contact'):
            user_id = contact.get('id')
            username = contact.get('username')
            display_name = contact.get('display_name')

            contact_item = DirectoryItem(display_name, context.create_uri(['user', user_id]))

            # portraits
            portraits = contact.find('portraits')
            if portraits is not None:
                for portrait in portraits.iter('portrait'):
                    height = int(portrait.get('height', '0'))
                    if height >= 256:
                        contact_item.set_image(portrait.text)
                        break
                    pass
                pass

            contact_item.set_fanart(provider.get_fanart(context))
            result.append(contact_item)
            pass
        pass

    return result