import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from yt_dlp.utils import DownloadError

from reddit_downloader.cli import main
from reddit_downloader.downloader import RedditDownloadError, download_video


URL = "https://www.reddit.com/r/example/comments/abc123/post/"


class AuthenticationTests(unittest.TestCase):
    def test_cookie_sources_reach_extractor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cookiefile = root / "cookies.txt"
            cookiefile.write_text("# Netscape HTTP Cookie File\n")
            for kwargs, key, expected in (
                ({"cookies_from_browser": "firefox"}, "cookiesfrombrowser", ("firefox",)),
                ({"cookies": cookiefile}, "cookiefile", str(cookiefile)),
                ({}, "cookiesfrombrowser", None),
            ):
                with self.subTest(kwargs=kwargs), patch(
                    "reddit_downloader.downloader.which", return_value="ffmpeg"
                ), patch("reddit_downloader.downloader.YoutubeDL") as extractor:
                    extractor.return_value.__enter__.return_value.download.return_value = 0
                    download_video(URL, root, **kwargs)
                    self.assertEqual(extractor.call_args.args[0].get(key), expected)
                    extractor.return_value.__enter__.return_value.download.assert_called_once_with([URL])

    def test_login_failure_explains_retry(self):
        with tempfile.TemporaryDirectory() as directory, patch(
            "reddit_downloader.downloader.which", return_value="ffmpeg"
        ), patch("reddit_downloader.downloader.YoutubeDL") as extractor:
            extractor.return_value.__enter__.return_value.download.side_effect = DownloadError(
                "Account authentication is required"
            )
            with self.assertRaisesRegex(RedditDownloadError, "--cookies-from-browser firefox"):
                download_video(URL, Path(directory))

    def test_cli_passes_browser(self):
        with patch("reddit_downloader.cli.download_video") as download:
            self.assertEqual(main([URL, "--cookies-from-browser", "chrome"]), 0)
            self.assertEqual(download.call_args.kwargs["cookies_from_browser"], "chrome")

    def test_missing_cookie_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "Cookies file does not exist"):
                download_video(URL, Path(directory), cookies=Path(directory) / "missing.txt")


if __name__ == "__main__":
    unittest.main()
