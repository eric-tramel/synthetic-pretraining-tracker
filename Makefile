.PHONY: build clean

build:
	uv run build.py

clean:
	rm -f index.html
