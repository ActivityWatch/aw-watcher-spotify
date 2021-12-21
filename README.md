aw-watcher-spotify
==================

Watches your currently playing Spotify track. This is on a per-user basis since it uses the Spotify Web API, so you don't need to run it on all your machines if you don't want the redundancy.

This watcher is currently in a early stage of development, please submit PRs if you find bugs!


## Usage

### Step 0: Create Spotify Web API token

Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications) and create a new application.

In the app settings, add `http://localhost:8088` in the Redirect URIs section.

### Step 1: Install package (using poetry)

Requirements: Requires that you have poetry installed.

First install the package and its dependencies:

```sh
poetry install
```

First run (generates empty config that you need to fill out):

```sh
poetry run aw-watcher-spotify
```
### Step 1: Install package (without poetry, using only pip)

Install the requirements:

```sh
pip install .
```

First run (generates empty config that you need to fill out):
```sh
python aw-watcher-spotify/main.py
```

### Step 2: Enter credentials

If this is the first time you run it on your machine, it will give you an error, this is normal.
Just fill in the config file (the directory is referenced in the error).

Run the script again and...
You're done! Try playing a song on Spotify on any of your devices and it should start logging (provided they are not in offline mode).


## Note

Even without using this watcher, you can get a full export of the last year of listening history by requesting an export directly from Spotify here: https://www.spotify.com/us/account/privacy/

The export contains, among other things:

- **Streaming history for the past year**
- Playlists
- Search queries
- A list of items saved in your library
- User data
- Inferences

(thanks [@oreHGA](https://github.com/oreHGA) for the tip!)
