import sys
import os

path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, "..")
sys.path.insert(0, path)

import aw_watcher_spotify

aw_watcher_spotify.main()
