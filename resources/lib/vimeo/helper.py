from resources.lib.kodion.items import VideoItem

__author__ = 'bromix'

import xml.etree.ElementTree as ET


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
        current_page = int(videos.get('page', '1'))
        total_videos = int(videos.get('total', '1'))

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
        pass
    return result