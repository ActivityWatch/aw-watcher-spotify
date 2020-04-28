aw-watcher-spotify
==================

Watches your currently playing Spotify track. This is on a per-user basis since it uses the Spotify Web API, so you don't need to run it on all your machines if you don't want the redundancy.

This watcher is currently in a early stage of development. It's not expected to work without a little tweaking.


## Usage

First install the package and its dependencies:

```sh
env PIP_USER=true make install
```

First run (generates empty config that you need to fill out):

```sh
python3 -m aw_watcher_spotify
```

If this is the first time you run it on your machine, it will give you an error, this is normal. Just fill in the config file referenced in the error. You can create the client credentials needed at the [Spotify Developer portal](https://beta.developer.spotify.com/). In the dashboard, go to your app settings and add `http://localhost/` in the Redirect URIs section.

Now run it again:

```sh
python3 -m aw_watcher_spotify
```

It will ask you to go to a URL (or try to open it for you), you need to paste the URL you're redirected to (something of the format `http://localhost/?code=...`) into the terminal.

You're done! Try playing a song on Spotify on any of your devices and it should start logging (provided they are not in offline mode).
