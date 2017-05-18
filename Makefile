.PHONY: build

build:
	true

install:
	pip3 install ${PIPARGS} .

test:
	python3 -c "import aw_watcher_spotify"
#	python3 -m aw_watcher_spotify --help

package:
	true

