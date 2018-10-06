#!/usr/bin/env python3

import json
import requests
import os
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify  # noqa: E402

plex_status_json = requests.get('http://tuxbox/tv/plex.php?type=status')
plex_status_data = json.loads(plex_status_json.content)
icon = os.path.dirname(os.path.realpath(__file__)) + '/plex.png'
notification_text = ''
y1_color = '#f4b042'
y2_color = '#e9a049'
y3_color = '#cc7b19'


def calculate_lenght(*args):
    line_length = 0
    for arg in args:
        line_length += len(arg)
    return line_length


def send_notification(title, text, full_path_to_icon=''):
    Notify.init('PlexNow')
    n = Notify.Notification.new(title, text, full_path_to_icon)
    n.show()


def progress(duration, offset, bar_len=20):
    filled_len = int(round(bar_len * offset / float(duration)))
    # percents = round(100.0 * offset / float(duration), 1)
    bar = '━' * filled_len + '<span color=\'#8c8c8c\'>' + '─' * \
        (bar_len - filled_len) + '</span>'
    return bar


def build_movie_string(title, year, duration, offset):
    movie_string = '<b><span color=\'' + y1_color +\
        '\'>' + title + '</span> (' + year + \
        ')</b>\n<span color=\'#cc7b19\'>' + \
        progress(int(duration), int(offset)) + '</span>'
    return movie_string


def build_episode_string(gp_title, p_title, title, duration, offset):
    episode_string = '<b><span color=\'' + y1_color + \
        '\'>' + gp_title.title() + '</span></b> › <b>' + p_title + \
        '</b> › <b><span color=\'' + y1_color + '\'>' + title + \
        '</span></b>\n<span color=\'#cc7b19\'>' +\
        progress(int(duration), int(offset)) + '</span>'
    return episode_string


def notify_text_builder(item):
    try:
        if item['type'] == 'movie':
            return build_movie_string(
                item['title'],
                item['year'],
                item['Media']['Part']['duration'],
                item['viewOffset'])
        elif item['type'] == 'episode':
            return build_episode_string(
                item['grandparentTitle'],
                item['parentTitle'],
                item['title'],
                item['Media']['Part']['duration'],
                item['viewOffset'])
    except (KeyError, IndexError) as e:
        return '<b><span color=\'{}\'>No such Key: {}</span></b>'.format(
            y1_color,
            e)


if isinstance(plex_status_data, list):
    for item in plex_status_data:
        notification_text += '\n\n' + notify_text_builder(item)
elif isinstance(plex_status_data, dict):
    notification_text = notify_text_builder(plex_status_data)
else:
    notification_text = '<b>No media playing</b>'
    print(notification_text)

send_notification("PlexNow", notification_text, icon)

Notify.uninit()
