import importlib
import os
import unittest
from unittest.mock import Mock, patch

from spotipy.exceptions import SpotifyException

watcher_main = importlib.import_module("aw_watcher_spotify.main")


class AuthTests(unittest.TestCase):
    @patch.object(watcher_main, "Spotify")
    @patch.object(watcher_main, "SpotifyOAuth")
    @patch.object(watcher_main, "CacheFileHandler")
    @patch.object(watcher_main.dirs, "get_cache_dir")
    def test_auth_uses_activitywatch_cache_dir(
        self, get_cache_dir, cache_handler_cls, oauth_cls, spotify_cls
    ):
        get_cache_dir.return_value = "/tmp/activitywatch/aw-watcher-spotify"

        watcher_main.auth("alice", "client-id", "client-secret")

        cache_handler_cls.assert_called_once_with(
            cache_path=os.path.join(
                "/tmp/activitywatch/aw-watcher-spotify", "spotify-token-cache"
            )
        )
        oauth_kwargs = oauth_cls.call_args.kwargs
        self.assertIs(oauth_kwargs["cache_handler"], cache_handler_cls.return_value)
        self.assertNotIn("cache_path", oauth_kwargs)
        self.assertEqual(
            set(oauth_kwargs["scope"].split()),
            {"user-read-currently-playing", "user-read-playback-state"},
        )
        spotify_cls.assert_called_once_with(auth_manager=oauth_cls.return_value)


class PollingTests(unittest.TestCase):
    def test_retry_delay_is_exponential_and_capped(self):
        self.assertEqual(watcher_main.retry_delay(1, 5.0), 5.0)
        self.assertEqual(watcher_main.retry_delay(3, 5.0), 20.0)
        self.assertEqual(watcher_main.retry_delay(20, 5.0), 300.0)

    def test_poll_refreshes_access_token_after_401(self):
        spotify = Mock()
        spotify.currently_playing.side_effect = [
            SpotifyException(401, -1, "expired token"),
            {"is_playing": True, "item": {}},
        ]
        spotify.auth_manager.get_cached_token.return_value = {
            "refresh_token": "refresh-me"
        }

        returned_spotify, track = watcher_main.poll_current_track(
            spotify, "alice", "client-id", "client-secret"
        )

        self.assertIs(returned_spotify, spotify)
        self.assertTrue(track["is_playing"])
        spotify.auth_manager.refresh_access_token.assert_called_once_with("refresh-me")
        self.assertEqual(spotify.currently_playing.call_count, 2)

    @patch.object(watcher_main, "auth")
    def test_poll_reauthenticates_when_no_refresh_token_exists(self, auth):
        expired_spotify = Mock()
        expired_spotify.currently_playing.side_effect = SpotifyException(
            401, -1, "expired token"
        )
        expired_spotify.auth_manager.get_cached_token.return_value = None
        replacement_spotify = Mock()
        replacement_spotify.currently_playing.return_value = {
            "is_playing": True,
            "item": {},
        }
        auth.return_value = replacement_spotify

        returned_spotify, track = watcher_main.poll_current_track(
            expired_spotify, "alice", "client-id", "client-secret"
        )

        self.assertIs(returned_spotify, replacement_spotify)
        self.assertTrue(track["is_playing"])
        auth.assert_called_once_with("alice", "client-id", "client-secret")


if __name__ == "__main__":
    unittest.main()
