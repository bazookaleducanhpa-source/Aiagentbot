"""Replay a TikTok video in a visible browser; playback is not a confirmed view."""
import argparse
import math
import re
import sys
import time
from urllib.parse import urlsplit, urlunsplit


def video_url(value):
    parts = urlsplit(value.strip())
    if (parts.scheme != "https" or parts.netloc not in {"www.tiktok.com", "tiktok.com"}
            or not re.fullmatch(r"/@[^/]+/video/\d+/?", parts.path)):
        raise argparse.ArgumentTypeError(
            "Use a full link: https://www.tiktok.com/@user/video/123456789")
    return urlunsplit(("https", "www.tiktok.com", parts.path.rstrip("/"), "", ""))


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("Must be at least 1.")
    return number


def positive_seconds(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("Must be a finite number greater than 0.")
    return number


def parse_args(argv=None, url_validator=video_url, description=__doc__):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("url", type=url_validator)
    parser.add_argument("--repeat", type=positive_int, default=3,
                        help="Number of playback attempts (default: 3)")
    parser.add_argument("--seconds", type=positive_seconds, default=30,
                        help="Maximum playback time per attempt (default: 30)")
    parser.add_argument("--timeout", type=positive_seconds, default=60,
                        help="Maximum time to wait for loading or stalled media (default: 60)")
    parser.add_argument("--channel", choices=("chrome", "msedge"),
                        help="Use an installed browser instead of Playwright Chromium")
    parser.add_argument("--ready", action="store_true",
                        help="Pause first so you can dismiss dialogs or log in manually")
    return parser.parse_args(argv)


# Choose the largest visible video, rather than a hidden preload or suggestion.
START_VIDEO = """async () => {
    if (document.querySelector('.html5-video-player.ad-showing')) return false;
    const candidates = [...document.querySelectorAll('video')].map(v => {
        const r = v.getBoundingClientRect();
        const w = Math.max(0, Math.min(r.right, innerWidth) - Math.max(r.left, 0));
        const h = Math.max(0, Math.min(r.bottom, innerHeight) - Math.max(r.top, 0));
        return {v, area: w * h};
    }).filter(x => x.area > 0).sort((a, b) => b.area - a.area);
    if (!candidates.length) return false;
    const v = candidates[0].v;
    window.__playbackVideo = v;
    v.muted = true;
    v.loop = false;
    try { v.currentTime = 0; await v.play(); return true; }
    catch (_) { return false; }
}"""

VIDEO_STATE = """() => {
    const v = window.__playbackVideo;
    if (!v || !v.isConnected) return null;
    return {time: v.currentTime, ended: v.ended, paused: v.paused,
            ad: !!document.querySelector('.html5-video-player.ad-showing'),
            error: !!v.error, ready: v.readyState};
}"""


def start_video(page, timeout):
    from playwright.sync_api import Error

    start_deadline = time.monotonic() + timeout
    while True:
        try:
            if page.evaluate(START_VIDEO):
                break
        except Error as exc:
            # TikTok can navigate again after the first document has loaded.
            if "Execution context was destroyed" not in str(exc):
                raise
        if time.monotonic() >= start_deadline:
            raise RuntimeError("Video did not start. Check login, dialogs or verification in the browser.")
        page.wait_for_timeout(500)


def watch(page, seconds, timeout):
    from playwright.sync_api import Error

    start_video(page, timeout)
    played = 0.0
    previous = 0.0
    progress_deadline = time.monotonic() + timeout
    while played < seconds:
        page.wait_for_timeout(250)
        try:
            state = page.evaluate(VIDEO_STATE)
        except Error as exc:
            if "Execution context was destroyed" not in str(exc):
                raise
            state = None
        if state is None:
            # The application may replace its video element during hydration.
            remaining = progress_deadline - time.monotonic()
            if remaining <= 0:
                raise RuntimeError("Video disappeared and did not resume.")
            start_video(page, remaining)
            previous = 0.0
            continue
        if state["error"]:
            raise RuntimeError("Video reported a playback error.")
        delta = state["time"] - previous
        # Ignore seeks; count only normal media-clock progress.
        if not state["ad"] and 0 < delta < 1:
            played += delta
            progress_deadline = time.monotonic() + timeout
        previous = state["time"]
        if not state["ad"] and state["ended"]:
            if played <= 0:
                raise RuntimeError("Video ended without measurable playback.")
            return played
        if time.monotonic() >= progress_deadline:
            raise RuntimeError("Playback stalled. Resolve the browser prompt and run again.")
    page.evaluate("() => window.__playbackVideo?.pause()")
    return played


def main(argv=None, url_validator=video_url, description=__doc__, platform="TikTok"):
    args = parse_args(argv, url_validator, description)
    try:
        from playwright.sync_api import Error, sync_playwright
    except ImportError:
        print("Install: python -m pip install -r requirements-playback.txt", file=sys.stderr)
        return 1
    try:
        with sync_playwright() as playwright:
            options = {"headless": False}
            if args.channel:
                options["channel"] = args.channel
            browser = playwright.chromium.launch(**options)
            try:
                page = browser.new_page()
                print(f"Playback attempts are not confirmed {platform} views.", flush=True)
                for index in range(args.repeat):
                    page.goto(args.url, wait_until="domcontentloaded", timeout=args.timeout * 1000)
                    if index == 0 and args.ready:
                        input("Prepare the video in the browser, then press Enter here: ")
                    elapsed = watch(page, args.seconds, args.timeout)
                    print(f"Playback {index + 1}/{args.repeat}: {elapsed:.1f}s", flush=True)
                return 0
            finally:
                browser.close()
    except (Error, RuntimeError, EOFError) as exc:
        print(f"Stopped: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Stopped by user.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
