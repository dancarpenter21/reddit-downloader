"""Command line entry point."""

import argparse
from pathlib import Path
import sys

from .downloader import RedditDownloadError, download_video, validate_url


def reddit_url(value: str) -> str:
    try:
        return validate_url(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Download a video from a Reddit post or video link."
    )
    parser.add_argument("url", type=reddit_url, help="Reddit post or video URL")
    parser.add_argument(
        "-o", "--output-dir", type=Path, default=Path("downloads"),
        help="destination directory (default: ./downloads)",
    )
    auth = parser.add_mutually_exclusive_group()
    auth.add_argument(
        "--cookies-from-browser",
        choices=("brave", "chrome", "chromium", "edge", "firefox", "opera", "safari", "vivaldi", "whale"),
        metavar="BROWSER",
        help="read cookies from a browser logged in to Reddit (for example firefox or chrome)",
    )
    auth.add_argument(
        "--cookies", type=Path, metavar="FILE",
        help="read a Netscape-format cookies file",
    )
    args = parser.parse_args(argv)

    try:
        download_video(
            args.url, args.output_dir,
            cookies_from_browser=args.cookies_from_browser,
            cookies=args.cookies,
        )
    except (RedditDownloadError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nDownload cancelled.", file=sys.stderr)
        return 130
    return 0
