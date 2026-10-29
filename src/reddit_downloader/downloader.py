"""URL validation and media downloading, independent of the CLI."""

from pathlib import Path
from shutil import which
from urllib.parse import urlsplit

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


class RedditDownloadError(Exception):
    """A download could not be completed."""


def validate_url(url: str) -> str:
    """Require an HTTP(S) link on a Reddit domain."""
    url = url.strip()
    try:
        parsed = urlsplit(url)
        host = parsed.hostname or ""
        valid_host = (
            host == "reddit.com"
            or host.endswith(".reddit.com")
            or host in {"redd.it", "v.redd.it"}
        )
        if (
            parsed.scheme not in {"http", "https"}
            or not valid_host
            or parsed.username is not None
            or parsed.password is not None
            or parsed.port not in {None, 80, 443}
            or parsed.path in {"", "/"}
        ):
            raise ValueError
    except ValueError:
        raise ValueError("Provide a Reddit post or video URL starting with https://.") from None
    return url


def download_video(
    url: str,
    output_dir: Path,
    *,
    cookies_from_browser: str | None = None,
    cookies: Path | None = None,
) -> None:
    """Download the best available video and audio into output_dir."""
    url = validate_url(url)
    if cookies_from_browser and cookies is not None:
        raise ValueError("Choose either browser cookies or a cookies file.")
    if cookies is not None:
        cookies = cookies.expanduser().resolve()
        if not cookies.is_file():
            raise ValueError(f"Cookies file does not exist: {cookies}")
    if which("ffmpeg") is None:
        raise RedditDownloadError(
            "FFmpeg is required to combine video and audio. Install it and retry."
        )

    try:
        output_dir = output_dir.expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        options = {
            "paths": {"home": str(output_dir)},
            "outtmpl": "%(title).150B [%(id)s].%(ext)s",
            "format": "bv*+ba/b",
            "noplaylist": True,
            "overwrites": False,
            "restrictfilenames": True,
        }
        if cookies_from_browser:
            options["cookiesfrombrowser"] = (cookies_from_browser,)
        if cookies is not None:
            options["cookiefile"] = str(cookies)
        with YoutubeDL(options) as downloader:
            if downloader.download([url]) != 0:
                raise RedditDownloadError("The video download failed.")
    except DownloadError as exc:
        if any(term in str(exc).lower() for term in ("authentication", "login", "sign in")):
            raise RedditDownloadError(
                "Reddit requires a logged-in session for this request. Log in to Reddit "
                "in your browser, then retry with --cookies-from-browser firefox "
                "(or chrome). You can also use --cookies /path/to/cookies.txt with "
                "a Netscape-format cookies file. If you already supplied cookies, "
                "refresh the login and check that the account can view the post."
            ) from exc
        raise RedditDownloadError(str(exc)) from exc
    except OSError as exc:
        raise RedditDownloadError(str(exc)) from exc
