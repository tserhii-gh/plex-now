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


def calculate_lenght(*args):
    line_length = 0
    for arg in args:
        line_length += len(arg)
    return line_length


def send_notification(title, text, full_path_to_icon=''):
    Notify.init('PlexNow')
    n = Notify.Notification.new(title, text, full_path_to_icon)
    n.show()


def progress(count, total, bar_len=20):
    filled_len = int(round(bar_len * count / float(total)))
    # percents = round(100.0 * count / float(total), 1)
    bar = '▰' * filled_len + '▱' * (bar_len - filled_len)
    # bar = '⣿' * filled_len + '⣀' * (bar_len - filled_len)
    # bar = '▮' * filled_len + '▯' * (bar_len - filled_len)
    return bar


def notify_text_builder(item):
    try:
        if item['type'] == 'movie':
            total_length = calculate_lenght(item['title'],
                                            item['year'])
            text = '<b><span color=\'{}\'>{}</span> ({})</b>'.format(
                error_color,
                item['title'],
                item['year']
            )
            text += '\n<span color=\'#cc7b19\'>' + progress(int(item['viewOffset']), int(
                    item['Media']['Part']['duration']), total_length) + '</span>'
            return text
        elif item['type'] == 'episode':
            total_length = calculate_lenght(
                item['grandparentTitle'].title(),
                item['parentTitle'],
                item['title'])
            text = '<b><span color=\'{}\'>{}</span></b> › <b>{}</b> › <b><span color=\'{}\'>{}</span></b>'.format(
                error_color,
                item['grandparentTitle'].title(),
                item['parentTitle'],
                error_color,
                item['title'])
            text += '\n' + progress(int(item['viewOffset']), int(
                    item['Media']['Part']['duration']), total_length)
            return text

    except (KeyError, IndexError) as e:
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

send_notification("PlexNow", '\n' + notification_text, icon)

Notify.uninit()
