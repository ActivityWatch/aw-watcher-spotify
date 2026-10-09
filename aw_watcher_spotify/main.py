#!/usr/bin/env python3

import argparse
import json
import logging
import os
import sys
import traceback
from datetime import datetime, timedelta, timezone
from time import monotonic, sleep
from typing import Optional, Tuple

from requests import RequestException
from spotipy.exceptions import SpotifyException
from spotipy import Spotify
from spotipy.oauth2 import CacheFileHandler, SpotifyOAuth, SpotifyOauthError

from aw_core import dirs
from aw_core.models import Event
from aw_client.client import ActivityWatchClient
from aw_core.log import setup_logging


DEFAULT_CONFIG = """
[aw-watcher-spotify]
username = ""
client_id = ""
client_secret = ""
poll_time = 5.0"""

SPOTIFY_SCOPE = "user-read-currently-playing user-read-playback-state"
MAX_RETRY_SECONDS = 300.0
STALE_WARNING_SECONDS = 15 * 60


def get_current_track(sp) -> Optional[dict]:
    current_track = sp.currently_playing(additional_types=["episode"])
    if current_track and current_track["is_playing"]:
        return current_track
    return None


def data_from_track(track: dict, sp) -> dict:
    song_name = track["item"]["name"]
    data = {}
    data["title"] = song_name
    data["uri"] = track["item"]["uri"]

    if track["item"]["type"] == "track":
        artist_name = track["item"]["artists"][0]["name"]
        album_name = track["item"]["album"]["name"]
        data["popularity"] = track["item"].get("popularity", -1) or -1
        data["album"] = album_name
        data["artist"] = artist_name
        logging.debug("TRACK: {} - {} ({})".format(song_name, artist_name, album_name))
    elif track["item"]["type"] == "episode":
        publisher = track["item"]["show"]["publisher"]
        data["artist"] = publisher
        data["album"] = track["item"]["show"]["name"]
        logging.debug("EPISODE: {} - {}".format(song_name, publisher))

    return data


def auth(username: str, client_id: str, client_secret: str) -> Spotify:
    cache_path = os.path.join(
        dirs.get_cache_dir("aw-watcher-spotify"), "spotify-token-cache"
    )
    cache_handler = CacheFileHandler(cache_path=cache_path)
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://127.0.0.1:8088",
        scope=SPOTIFY_SCOPE,
        cache_handler=cache_handler,
    )
    return Spotify(auth_manager=auth_manager)


def retry_delay(failure_count: int, poll_time: float) -> float:
    base_delay = max(poll_time, 1.0)
    exponent = min(max(failure_count - 1, 0), 10)
    return min(base_delay * 2**exponent, MAX_RETRY_SECONDS)


def refresh_access_token(sp: Spotify) -> bool:
    token_info = sp.auth_manager.get_cached_token()
    refresh_token = token_info.get("refresh_token") if token_info else None
    if not refresh_token:
        return False
    sp.auth_manager.refresh_access_token(refresh_token)
    return True


def poll_current_track(
    sp: Spotify, username: str, client_id: str, client_secret: str
) -> Tuple[Spotify, Optional[dict]]:
    try:
        return sp, get_current_track(sp)
    except SpotifyException as error:
        if error.http_status != 401:
            raise

        logging.warning("Spotify access token was rejected; refreshing it")
        try:
            refreshed = refresh_access_token(sp)
        except (SpotifyOauthError, RequestException):
            logging.warning(
                "Spotify token refresh failed; reauthenticating", exc_info=True
            )
            refreshed = False

        if not refreshed:
            sp = auth(username, client_id, client_secret)
        return sp, get_current_track(sp)


def load_config():
    from aw_core.config import load_config_toml as _load_config

    return _load_config("aw-watcher-spotify", DEFAULT_CONFIG)


def print_statusline(msg):
    last_msg_length = (
        len(print_statusline.last_msg) if hasattr(print_statusline, "last_msg") else 0
    )
    print(" " * last_msg_length, end="\r")
    print(msg, end="\r")
    print_statusline.last_msg = msg


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--testing", action="store_true")
    argparser.add_argument("--verbose", action="store_true")
    args = argparser.parse_args()
    setup_logging(
        name="aw-watcher-spotify",
        testing=args.testing,
        verbose=args.verbose,
        log_stderr=True,
        log_file=True,
    )
    config_dir = dirs.get_config_dir("aw-watcher-spotify")

    config = load_config()
    poll_time = float(config["aw-watcher-spotify"].get("poll_time"))
    username = config["aw-watcher-spotify"].get("username", None)
    client_id = config["aw-watcher-spotify"].get("client_id", None)
    client_secret = config["aw-watcher-spotify"].get("client_secret", None)
    if not username or not client_id or not client_secret:
        logging.warning(
            "username, client_id or client_secret not specified in config file (in folder {}). Get your client_id and client_secret here: https://developer.spotify.com/my-applications/".format(
                config_dir
            )
        )
        sys.exit(1)

    aw = ActivityWatchClient("aw-watcher-spotify", testing=args.testing)
    bucketname = "{}_{}".format(aw.client_name, aw.client_hostname)
    aw.create_bucket(bucketname, "currently-playing", queued=True)
    aw.connect()

    try:
        sp = auth(username, client_id=client_id, client_secret=client_secret)
    except SpotifyOauthError:
        logging.exception("Spotify authentication failed")
        sys.exit(1)

    last_track = None
    track = None
    failure_count = 0
    last_successful_poll = monotonic()
    stale_warning_logged = False
    while True:
        try:
            sp, track = poll_current_track(sp, username, client_id, client_secret)
            # from pprint import pprint
            # pprint(track)
        except (
            json.JSONDecodeError,
            RequestException,
            SpotifyException,
            SpotifyOauthError,
        ) as error:
            failure_count += 1
            delay = retry_delay(failure_count, poll_time)
            logging.warning(
                "Spotify poll failed (%s): %s; retrying in %.1fs",
                type(error).__name__,
                error,
                delay,
            )
            if (
                not stale_warning_logged
                and monotonic() - last_successful_poll >= STALE_WARNING_SECONDS
            ):
                logging.warning(
                    "No successful Spotify response for at least %d minutes",
                    STALE_WARNING_SECONDS // 60,
                )
                stale_warning_logged = True
            sleep(delay)
            continue
        except Exception:
            failure_count += 1
            delay = retry_delay(failure_count, poll_time)
            logging.exception(
                "Unexpected Spotify poll failure; retrying in %.1fs", delay
            )
            sleep(delay)
            continue

        failure_count = 0
        last_successful_poll = monotonic()
        stale_warning_logged = False

        try:
            # Outputs a new line when a song ends, giving a short history directly in the log
            if last_track:
                last_track_data = data_from_track(last_track, sp)
                if not track or (
                    track
                    and last_track_data["uri"] != data_from_track(track, sp)["uri"]
                ):
                    song_td = timedelta(seconds=last_track["progress_ms"] / 1000)
                    song_time = int(song_td.seconds / 60), int(song_td.seconds % 60)
                    print_statusline(
                        "Track ended ({}:{:02d}): {title} - {artist} ({album})\n".format(
                            *song_time, **last_track_data
                        )
                    )

            if track:
                track_data = data_from_track(track, sp)
                song_td = timedelta(seconds=track["progress_ms"] / 1000)
                song_time = int(song_td.seconds / 60), int(song_td.seconds % 60)

                print_statusline(
                    "Current track ({}:{:02d}): {title} - {artist} ({album})".format(
                        *song_time, **track_data
                    )
                )

                event = Event(timestamp=datetime.now(timezone.utc), data=track_data)
                aw.heartbeat(bucketname, event, pulsetime=poll_time + 1, queued=True)
            else:
                print_statusline("Waiting for track to start playing...")

            last_track = track
        except Exception as e:
            print("An exception occurred: {}".format(e))
            traceback.print_exc()
        sleep(poll_time)


if __name__ == "__main__":
    main()
