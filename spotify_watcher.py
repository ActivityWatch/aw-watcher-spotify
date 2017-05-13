#!/usr/bin/env python3

import sys
import logging
from typing import Optional
from time import sleep
from datetime import datetime, timezone, timedelta

import spotipy
import spotipy.util as util

from aw_core.models import Event
from aw_client.client import ActivityWatchClient


def patch_spotipy():
    """Ugly but works until the Spotipy maintainer fixes his PR backlog"""
    def patch_current_track(self):
        return self._get('me/player/currently-playing')

    spotipy.Spotify.current_user_playing_track = patch_current_track


def get_current_track(sp) -> Optional[dict]:
        current_track = sp.current_user_playing_track()
        if current_track['is_playing']:
            return current_track
        else:
            return None


def data_from_track(track):
    song_name = track['item']['name']
    album_name = track['item']['album']['name']
    artist_name = track['item']['artists'][0]['name']
    logging.debug("{} - {} ({})".format(song_name, artist_name, album_name))
    data = {
        "title": song_name,
        "artist": artist_name,
        "album": album_name,
        "id": track['item']['id']
    }
    return data


def auth(username):
    scope = 'user-read-currently-playing'
    token = util.prompt_for_user_token(username, scope)

    if token:
        return spotipy.Spotify(auth=token)
    else:
        print("Was unable to get token")
        sys.exit(1)


def main():
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print("Usage: {} username".format(sys.argv[0]))
        sys.exit()

    patch_spotipy()

    poll_interval = 5

    aw = ActivityWatchClient('aw-watcher-spotify', testing=True)
    bucketname = "{}_{}".format(aw.client_name, aw.client_hostname)
    aw.setup_bucket(bucketname, 'currently-playing')
    aw.connect()

    sp = auth(username)
    while True:
        track = get_current_track(sp)
        track_data = data_from_track(track)
        song_td = timedelta(seconds=track['progress_ms'] / 1000)
        song_time = int(song_td.seconds / 60), int(song_td.seconds % 60)
        print("Current track ({}:{}): {title} - {artist} ({album})".format(*song_time, **track_data), end='\r')
        aw.heartbeat(bucketname, Event(timestamp=datetime.now(timezone.utc), data=track_data), pulsetime=poll_interval + 1)
        sleep(poll_interval)
    else:
        print("Can't get token for", username)


if __name__ == "__main__":
    main()
