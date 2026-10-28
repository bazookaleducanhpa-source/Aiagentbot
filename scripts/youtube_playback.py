"""Replay a YouTube video in a visible browser; playback is not a confirmed view."""
import argparse
import re
from urllib.parse import parse_qs, urlsplit

from tiktok_playback import main


def video_url(value):
    parts = urlsplit(value.strip())
    video_id = None
    if parts.scheme == "https":
        if parts.netloc in {"www.youtube.com", "youtube.com", "m.youtube.com"}:
            match = re.fullmatch(r"/shorts/([A-Za-z0-9_-]{11})/?", parts.path)
            if match:
                return f"https://www.youtube.com/shorts/{match.group(1)}"
            if parts.path == "/watch":
                video_id = parse_qs(parts.query).get("v", [None])[0]
        elif parts.netloc == "youtu.be":
            video_id = parts.path.strip("/")
    if video_id and re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        return f"https://www.youtube.com/watch?v={video_id}"
    raise argparse.ArgumentTypeError("Use a YouTube Shorts, watch, or youtu.be video URL.")


if __name__ == "__main__":
    raise SystemExit(main(url_validator=video_url, description=__doc__, platform="YouTube"))
