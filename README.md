aw-watcher-spotify
==================

Watches your currently playing Spotify track. This is on a per-user basis since it uses the Spotify Web API, so you don't need to run it on all your machines if you don't want the redundancy.

This watcher is currently in a early stage of development, please submit PRs if you find bugs!


## Usage

### Step 0: Create Spotify Web API token

Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications) and create a new application.

In the app settings, add `http://127.0.0.1:8088` in the Redirect URIs section.

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


## Viewing listening history

In ActivityWatch, open **Raw Data** and look for a populated
`aw-watcher-spotify_<hostname>` bucket. Use the full bucket ID, including the
hostname of the machine **running this watcher**, even if Spotify is playing on
another device. Select a date or time range when the watcher recorded playback.

### Top artists, tracks, or albums

In web UIs with **Top Bucket Data** (verified in desktop **v0.14.0b8**; not
available in **v0.13.2**):

1. Open **Activity**, select the watcher host and a date with listening data.
2. Choose **Edit view → Add visualization**.
3. Open the new card's gear menu and select **Top Bucket Data**.
4. Choose the full Spotify bucket ID under **Bucket**, then `artist`, `title`,
   or `album` under **Field in event data**.
5. Click **Save** to keep the card and its selections across reloads.

The totals are **recorded listening duration**, not play counts. Grouping by
`title` can combine different tracks with the same title.

### Older web UIs

On desktop **v0.13.2**, use **Timeline** to see recorded tracks chronologically,
or choose **Open** next to the Spotify bucket under **Raw Data** to inspect its
timeline and event fields. Set **Show from** and **to** to the relevant dates,
then click **Apply**. These paths do not require upgrading to a beta release.

**Custom Visualization** loads a separately served HTML page; it does not select
a data bucket. This watcher does not provide such a page, so entering
`aw-watcher-spotify` there cannot display its listening history.


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
