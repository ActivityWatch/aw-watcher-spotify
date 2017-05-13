#!/usr/bin/env python3

import sys
import logging
from typing import Optional
from time import sleep
from datetime import datetime, timezone

import spotipy
import spotipy.util as util

from aw_core.models import Event
from aw_client.client import ActivityWatchClient


def get_current_track(sp) -> Optional[dict]:
        current_track = sp.current_user_playing_track()
        if current_track['is_playing']:
            # print(current_track)
            # print(current_track['item'])
            # from pprint import pprint
            # pprint(current_track['item'])
            song_name = current_track['item']['name']
            album_name = current_track['item']['album']['name']
            artist_name = current_track['item']['artists'][0]['name']
            logging.debug("{} - {} ({})".format(song_name, artist_name, album_name))
            data = {
                "title": song_name,
                "artist": artist_name,
                "album": album_name,
                "id": current_track['item']['id']
            }
            # pprint(data)
            return data
        else:
            return None


def auth(username):
    scope = 'user-read-currently-playing'
    token = util.prompt_for_user_token(username, scope)

    if token:
        return spotipy.Spotify(auth=token)
    else:
        print("Was unable to get token")
        sys.exit(1)


def main():
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print("Usage: {} username".format(sys.argv[0]))
        sys.exit()

    logging.basicConfig(level=logging.INFO)

    poll_interval = 5

    aw = ActivityWatchClient('aw-watcher-spotify', testing=True)
    bucketname = "{}_{}".format(aw.client_name, aw.client_hostname)
    aw.setup_bucket(bucketname, 'currently-playing')
    aw.connect()

    sp = auth(username)
    while True:
        print("Polling...")
        track_data = get_current_track(sp)
        aw.heartbeat(bucketname, Event(timestamp=datetime.now(timezone.utc), data=track_data), pulsetime=poll_interval + 1)
        print("Heartbeat sent")
        sleep(poll_interval)
    else:
        print("Can't get token for", username)


if __name__ == "__main__":
    main()
