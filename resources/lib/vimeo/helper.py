from resources.lib.kodion.items import VideoItem, NextPageItem

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


def do_xml_video_response(context, provider, xml):
    result = []
    root = ET.fromstring(xml)

    status = root.get('stat')
    if status == 'fail':
        error_item = root.find('err')
        if error_item is not None:
            message = error_item.get('msg')
            explanation = error_item.get('expl')
            message = '%s - %s' % (message, explanation)
            context.get_ui().show_notification(message, time_milliseconds=15000)
            pass
        pass

    videos = root.find('videos')
    if videos is not None:
        for video in videos.iter('video'):
            video_id = video.get('id')
            title = video.find('title').text
            video_item = VideoItem(title, context.create_uri(['play'], {'video_id': video_id}))

            # plot
            plot = video.find('description').text
            if plot is not None:
                video_item.set_plot(plot)
                pass

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

        if len(result) > 0:
            current_page = int(videos.get('page', '1'))
            videos_per_page = int(videos.get('perpage', '1'))
            total_videos = int(videos.get('total', '1'))
            if videos_per_page * current_page < total_videos:
                next_page_item = NextPageItem(context, current_page)
                next_page_item.set_fanart(provider.get_fanart(context))
                result.append(next_page_item)
                pass
            pass
        pass
    return result