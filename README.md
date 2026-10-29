# Reddit Downloader

A Python command line tool that takes a Reddit post or video link and downloads
the video, including audio when available.

Python keeps the application small and provides access to
[yt-dlp](https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp) for media extraction.
FFmpeg combines separate video and audio streams.

## Requirements

- Python 3.10 or newer
- uv for Python environment and dependency management
- [FFmpeg](https://ffmpeg.org/download.html) installed and available on your PATH

## Installation

Run from the project directory:

```sh
uv sync
```

This creates the project environment in `.venv` and installs the dependencies
from `uv.lock`. Use `uv run` to run commands in that environment.
Install FFmpeg separately using your operating system's package manager or the
downloads linked above (for example, `sudo apt install ffmpeg` on Ubuntu or
`brew install ffmpeg` on macOS).

## Usage

Replace the example URL with a real Reddit post containing a video:

```sh
uv run reddit-downloader "https://www.reddit.com/r/subreddit/comments/post_id/title/"
uv run reddit-downloader "https://v.redd.it/video_id" --output-dir ./downloads
uv run python -m reddit_downloader --help
```

Files go into `./downloads` by default. The directory is created as needed.
Filenames include the title and media ID; existing completed files are not
overwritten. The downloader chooses the best available video and audio, so the
output extension depends on the source formats. Silent videos remain silent.

If Reddit asks for a login, sign in to Reddit in Firefox or Chrome on the same
machine, verify you can open the post, and pass that browser's cookies:

```sh
uv run reddit-downloader "https://www.reddit.com/r/subreddit/comments/post_id/title/" --cookies-from-browser firefox
# Or use Chrome:
uv run reddit-downloader "https://www.reddit.com/r/subreddit/comments/post_id/title/" --cookies-from-browser chrome
# Or an exported Netscape-format cookies file:
uv run reddit-downloader "https://www.reddit.com/r/subreddit/comments/post_id/title/" --cookies ~/cookies.txt
```

Choose one cookie option per run. Browser cookies must be accessible to the user
running the command; if browser storage is locked, close the browser and retry.
Treat exported cookies like passwords and keep them out of source control.
The app uses your existing session and does not ask for your Reddit password.

Deleted posts, private communities your account cannot access, or Reddit network
restrictions can still prevent downloads. There is no built-in browser, login
flow, or bulk subreddit scraping.
If extraction stops working after Reddit changes, update the dependency:

```sh
uv sync --upgrade-package yt-dlp
```

## Project layout

```text
reddit-downloader/
├── pyproject.toml                 # Package metadata, dependencies, CLI entry point
├── uv.lock                        # Resolved dependency versions
├── README.md                     # Setup and usage
├── .gitignore
└── src/
    └── reddit_downloader/
        ├── __init__.py
        ├── __main__.py            # python -m reddit_downloader
        ├── cli.py                 # Arguments and user-facing errors
        └── downloader.py          # URL validation and yt-dlp integration
```

Keep command line behavior in `cli.py` and download behavior in `downloader.py`
so future interfaces can reuse the same download function.
