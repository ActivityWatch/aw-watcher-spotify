.PHONY: build

build:
	true

install:
	pip3 install --process-dependency-links ${PIPARGS} .

install-user:
	make install PIPARGS="--user --editable"

uninstall:
	pip3 uninstall -y aw-watcher-spotify

test:
	python3 -c "import aw_watcher_spotify"
#	python3 -m aw_watcher_spotify --help

package:
	true

