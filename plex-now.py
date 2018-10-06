#!/usr/bin/env python3

import json
import requests
import os
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify

plex_status_json = requests.get('http://tuxbox/tv/plex.php?type=status')
plex_status_data = json.loads(plex_status_json.content)
icon = os.path.dirname(os.path.realpath(__file__)) + '/plex.png'
notification_text = ''
error_color = '#f4b042'


def send_notification(title, text, full_path_to_icon=''):
    Notify.init('PlexNow')
    n = Notify.Notification.new(title, text, full_path_to_icon)
    n.show()


def notify_text_builder(item):
    try:
        if item['type'] == 'movie':
            return '<b><span color=\'{}\'>{}</span> ({})</b>'.format(
                error_color,
                item['title'],
                item['year']
            )
        elif item['type'] == 'episode':
            return '<b><span color=\'{}\'>{}</span></b> › <b>{}</b> › <b><span color=\'{}\'>{}</span></b>'.format(
                error_color,
                item['grandparentTitle'].title(),
                item['parentTitle'],
                error_color,
                item['title'])
    except KeyError as e:
        return '<b><span color=\'{}\'>No such Key: {}</span></b>'.format(
            error_color,
            e)


if isinstance(plex_status_data, list):
    for item in plex_status_data:
        notification_text = notify_text_builder(item)
elif isinstance(plex_status_data, dict):
    notification_text = notify_text_builder(plex_status_data)
else:
    notification_text = '<b>No media playing</b>'
    print(notification_text)

send_notification("PlexNow", notification_text, icon)

Notify.uninit()
