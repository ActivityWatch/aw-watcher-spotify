.PHONY: build

build:
	poetry install

test:
	which aw-watcher-spotify
	python3 -c "import aw_watcher_spotify"

package:
	true

