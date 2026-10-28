# Dreamforge Studio

## Cappy Remake Studio (local)

Paste a reference video link into the separate remake workspace at **http://127.0.0.1:8010**. Start it from this project on Windows:

```powershell
./start-remake.ps1
```

The workflow creates an original English explainer with the white Cappy mascot, illustrations and animation, narration, cheerful library music and sound effects. Jobs and reusable voice caches live in `data/remake-jobs/`; the UI shows progress and available preview/export files. No external publishing is performed.

To start a job from a terminal, use the project's Python environment:

```powershell
python -m remake_studio.cli "https://www.youtube.com/watch?v=0NY2gAftzJE"
```

The reusable [cappy-video-remake skill](skills/cappy-video-remake/SKILL.md) defines agent responsibilities, visual timing, provenance and QA. Its workspace helper accepts `CAPPY_WORKSPACE` when this repository is moved. Existing Dreamforge workflows below remain available on port 8000.

### Source code and local production files

Git contains source, dependency manifests, tests and reusable skill instructions. `output/`, `data/`, `tmp/`, `node_modules/`, `.tools/`, secrets and user-owned media remain local. Ignoring these paths does not delete them. Back up finished videos, subtitles, editable job folders, voice caches, music and mascot artwork separately.

For a new checkout, install Python requirements from `requirements.txt` and `requirements-remake.txt`, then run `npm ci --prefix tools/motion-studio` for the shared Remotion runtime. The current Windows pipeline also expects the documented local FFmpeg executable and dedicated audio/model environments under `.tools/`; those installed environments and model weights are not bundled in Git. Restore the user's music library and mascot references at their documented paths before video production. Generated job projects link to the shared Node runtime instead of copying it.

`scripts/build_black_hole_subtitles.py` exports external multilingual SRT files from measured narration timings; its current inputs are the local black-hole revision job and sentence translations under that video's output folder. `scripts/rebuild_black_holes_v2.py` and `scripts/preview_cappy_conversational.py` reproduce that specific revision and require its preserved local job/assets.

A local AI entertainment studio: research → English story → illustrated vertical video with English narration → review → YouTube upload + TikTok publishing via Buffer (or manual kit).

**Vietnamese step-by-step API guide:** [API_SETUP_VI.md](docs/API_SETUP_VI.md). Includes Google OAuth and Buffer channel helper scripts.

**Vietnamese end-to-end guide for the current 3D kids-video workflow:** [HUONG_DAN_TU_DAU_DEN_CUOI.md](docs/HUONG_DAN_TU_DAU_DEN_CUOI.md). Covers setup, Google Flow, existing songs, publishing to both platforms, and the first-view growth plan.

## Run on Windows

Requires Python 3.11+:

```powershell
./start.ps1
```

Open **http://127.0.0.1:8000**. The script creates a virtual environment and installs dependencies. Manual setup:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Linux/macOS: use `python3` and `.venv/bin/python` instead.

Demo is default, requiring **no credentials**. Create a story, wait for `review`, preview/download the MP4, optionally edit the storyboard, then approve. Queue a simulated YouTube upload or export the TikTok kit. Demo uses a sample English story, geometric slides, silent audio and a watermark. It does not call external APIs or post externally.

## Live mode

Copy `.env.example` to `.env`, set `APP_MODE=live` and `OPENAI_API_KEY`, then restart. Each job calls:

- GPT-6 Luna for research analysis (`RESEARCH_MODEL`).
- GPT-6.1 Sol for English scripts (`CONTENT_MODEL`).
- GPT Image 2.5 Flare for one original image per scene (`IMAGE_MODEL`, low quality).
- OpenAI speech for English narration (`gpt-4o-mini-tts`), or ElevenLabs.
- Local FFmpeg for 720×1280 video, slow camera zoom, scene text and SRT captions.

This animates still images, not cinematic text-to-video. Character consistency is prompted, not guaranteed. Actual narration length may differ from target length. Paid API usage is separate from Plus. No hard dollar budget or exact cost estimator is included: limit jobs and set provider spending caps. Re-rendering calls image/speech APIs again. Paid calls are not automatically retried. Model availability or organization verification may affect access.

For ElevenLabs set `TTS_PROVIDER=elevenlabs`, `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID`. The speech model is `eleven_multilingual_v2`.

## Research

Set `YOUTUBE_API_KEY` for YouTube metadata. Optionally set `APIFY_API_TOKEN` for keyword research through the Clockworks TikTok Scraper: up to 12 results from the past week, no creator video downloads. `APIFY_MAX_CHARGE_USD` defaults to 0.5 per actor run. These are third-party metadata, not watched videos, transcripts or a For You feed scan. Without either provider, live research uses imported sources or reports no verified trend.

Import YouTube/TikTok URLs, summaries, dates and views in **Research sources**. Updating a source replaces its stats. Research runs save observations; repeat with updated counts to calculate growth/hour. Snapshots must be at least a minute apart. Otherwise lifetime views/hour is only a rough proxy. Imported sources are shared across the workspace; choose relevant ones.

## YouTube uploads

1. Enable YouTube Data API v3 in Google Cloud and configure OAuth consent.
2. Create a Desktop OAuth client, download JSON to `data/google-client.json`, then run `.venv/Scripts/python.exe scripts/connect_youtube.py`. It opens Google consent and saves credentials to `.env` without printing tokens. The requested scope is `https://www.googleapis.com/auth/youtube.upload`.
3. Store `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN` in `.env`; restart. Never share tokens in chat or public pages.
4. Approve a live video, select privacy and optional future local date, then queue it. Upload runs at that time, not via YouTube `publishAt`.

Keep the server running. Queues persist and overdue work runs after restart. Use **one process**, without `--workers` or reload. Interrupted renders become `failed`; interrupted uploads become `unknown`. Check YouTube Studio before further action. Resumable sessions are initialized but interrupted byte uploads are not resumed. Each job/platform can post once; published/ambiguous jobs cannot be edited.

Default privacy is **private**. Public upload depends on project audit and permissions; unaudited projects can be restricted to private. Metadata declares synthetic content and not made for kids; the channel targets a general audience. Review these settings for your actual content and audience before public use.

## TikTok

Choose **Manual** to export the MP4/caption/SRT kit, or **Buffer** for automatic posting. Configure `BUFFER_API_KEY`, `BUFFER_TIKTOK_CHANNEL_ID`, and Cloudinary cloud name/key/secret. Find channel IDs with `.venv/Scripts/python.exe scripts/list_buffer_channels.py`. Set `TIKTOK_PUBLISHER=buffer` to select that mode by default.

Live Buffer publishing requires **Public** consent: the approved MP4 is signed-uploaded to public Cloudinary hosting, then submitted to Buffer with TikTok AI disclosure and automatic scheduling. Cloudinary media persists until you delete it. The local queue submits at the selected time; Buffer gets at least one minute to ingest the video. `submitted` is not `published`; use **Check Buffer status** to confirm a `sent` result. Manage submitted schedules in Buffer. Editing is blocked once an external queue has accepted the video.

Account/API access and platform eligibility still apply. Direct TikTok posting is not implemented because internal tools cannot assume audit approval. Optional research uses Apify, not Buffer. Demo Buffer mode never contacts Buffer or uploads to Cloudinary. Existing queued TikTok entries keep their original manual behavior across configuration changes.

## Skills and feedback

Role instructions live in `skills/`. Edit research/content instructions in **Agent skills** (persisted in SQLite). Production/publisher cards are read-only references to code behavior.

Enter real views, retention and notes in **Performance feedback**. Future scripts include the latest eight live-job records; demo feedback is excluded. This is a prompt feedback loop, not model retraining or proven autonomous improvement. Automatic analytics synchronization and A/B testing are not included.

## Local operation

- Data: `data/studio.db`; files: `data/artifacts/<job-id>/`.
- Secrets: `.env`, excluded from git and never returned by settings endpoints.
- Single-user local app; bind to `127.0.0.1`. No public deployment or multi-user login.
- Bundled FFmpeg via `imageio-ffmpeg`; optionally set `FFMPEG_PATH`.
- Editing cancels queued posts and revokes approval.
- Two generation workers; max four unfinished jobs. No unattended recurring production; publication scheduling is supported.

## Verify

```powershell
python -m unittest discover -s tests -v
node --check web/app.js
```

Tests use temporary storage and mock providers, plus real demo MP4 rendering. Live integrations need credentials and are not exercised by offline tests.

## Official references

- [OpenAI text](https://developers.openai.com/api/docs/guides/text), [images](https://developers.openai.com/api/docs/guides/image-generation), [speech](https://developers.openai.com/api/docs/guides/text-to-speech)
- [ElevenLabs speech](https://elevenlabs.io/docs/api-reference/text-to-speech/convert)
- [YouTube search](https://developers.google.com/youtube/v3/docs/search/list), [upload](https://developers.google.com/youtube/v3/docs/videos/insert)
- [TikTok content sharing](https://developers.tiktok.com/docs/en/content-sharing-guidelines)
- [Buffer video API](https://developers.buffer.com/examples/create-video-post.html), [TikTok with Buffer](https://support.buffer.com/en-us/articles/using-tiktok-with-buffer-oGEroY9Of2)
- [Cloudinary signed uploads](https://cloudinary.com/documentation/authentication_signatures)
- [Apify TikTok actor](https://apify.com/clockworks/tiktok-scraper)
