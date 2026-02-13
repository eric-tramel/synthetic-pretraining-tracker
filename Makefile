.PHONY: build clean

build:
	uv run build.py

clean:
	rm -rf site/
