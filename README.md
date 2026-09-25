# Mahanavi Spirituals — Daily Devotional Content Pipeline

Automated system that, every day at 5:00 AM IST, selects a devotional
image for the day's deity (based on weekday), fetches Telugu Panchang
data, renders a branded image, generates Telugu SEO content, and
publishes it as a YouTube Community Post, Telegram channel post, and
(optionally) Facebook/Instagram posts — then sends you a Telegram
notification with the result.

## Table of contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Configuration reference](#configuration-reference)
- [Running it](#running-it)
- [Testing](#testing)
- [Docker](#docker)
- [Extending the system](#extending-the-system)
- [Known limitations — read before relying on this daily](#known-limitations--read-before-relying-on-this-daily)

## Architecture

Every external dependency (Panchang source, publish target, notifier) sits
behind an abstract interface in `core/interfaces.py`. `bootstrap.py` is
the *only* file that wires concrete implementations together — swapping
any component means changing one line there, nothing else.

```
src/mahanavi/
├── config.py              # Settings — loaded from .env, validated at startup
├── logging_config.py      # Rotating file + console logging
├── exceptions.py          # Exception hierarchy used across the whole app
├── retry.py                # Generic exponential-backoff decorator
├── text_utils.py           # Shared text-fitting helper (Telegram char limits)
├── pipeline.py              # DailyPipeline — the orchestrator
├── scheduler.py             # APScheduler cron wiring
├── bootstrap.py              # Composition root: builds DailyPipeline from Settings
├── main.py                    # CLI entrypoint (--run-now or the scheduler loop)
├── core/
│   ├── models.py            # Domain dataclasses (PanchangData, SeoContent, ...)
│   └── interfaces.py         # ABCs every concrete component implements
├── database/
│   ├── db.py                 # SQLite connection + schema
│   └── repositories.py        # ImageHistoryRepository, PostLogRepository
├── images/
│   ├── selector.py            # RandomImageSelector — non-repeating rotation
│   ├── renderer.py             # PillowImageRenderer — the branded image
│   ├── fonts.py                 # Telugu font loading (RAQM shaping)
│   ├── layout.py                 # Low-level Pillow drawing helpers
│   └── telugu_text.py             # Telugu weekday/month/deity vocabulary
├── panchang/
│   ├── dummy_provider.py          # Offline, deterministic — for dev/testing
│   ├── api_provider.py             # Generic REST API client
│   ├── scraper_provider.py          # BeautifulSoup scraper (config-driven selectors)
│   └── factory.py                    # Picks a provider based on Settings
├── content/
│   ├── data.py                        # Deity-specific Telugu phrases/hashtags/keywords
│   └── generator.py                    # Assembles the final SEO content
├── publishers/
│   ├── telegram_uploader.py            # Official Bot API
│   ├── facebook_uploader.py             # Official Graph API
│   ├── instagram_uploader.py             # Official Graph API (2-step publish)
│   ├── youtube_playwright_uploader.py     # Browser automation (no API exists)
│   ├── youtube_selectors.py                # Studio UI selectors — verify these!
│   └── factory.py                            # Builds the enabled publisher list
├── notifications/
│   ├── telegram_notifier.py                  # Real operator alerts
│   └── logging_notifier.py                    # Fallback if not configured
└── scripts/
    └── youtube_login_setup.py                  # One-time manual login capture
```

## Prerequisites

- Python 3.13
- A Telegram bot (via [@BotFather](https://t.me/BotFather)) — required
- A YouTube channel you can log into — required for the YouTube target
- (Optional) A Meta Developer App — only if you enable Facebook/Instagram
- Docker, if you want to deploy that way (see [Docker](#docker))

## Setup

### 1. Clone and install

```bash
git clone <your-repo-url>
cd mahanavi-spirituals
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install --with-deps chromium
```

### 2. Add your devotional images

Drop your actual images into the matching weekday folder (the `.gitkeep`
files are just placeholders — delete them once you've added real images):

```
Images/
├── Monday_Shiva/
├── Tuesday_Hanuman/
├── Wednesday_Ganesha/
├── Thursday_Sai/
├── Friday_Lakshmi/
├── Saturday_Venkateswara/
└── Sunday_Surya/
```

Folder names must stay in this exact `Weekday_DeityName` format — the
image selector and content generator both parse the deity from it.

### 3. Configure

```bash
cp .env.example .env
```

Then edit `.env` — see [Configuration reference](#configuration-reference)
below for what each section needs. **Leave a variable blank rather than
setting it to a placeholder string** — blank is treated as "not set";
this is safer than a fake value that might pass validation but fail at
runtime.

### 4. Set up Telegram (required)

1. Message [@BotFather](https://t.me/BotFather), create a bot, copy its
   token into `MAHANAVI_TELEGRAM_BOT_TOKEN`.
2. Add the bot as an **admin** of your channel (needed to post there).
   Set `MAHANAVI_TELEGRAM_CHANNEL_ID` to your channel's `@username`.
3. For notifications: message your bot once from your own account (or a
   private ops group), then visit
   `https://api.telegram.org/bot<TOKEN>/getUpdates` to find that chat's
   ID. Set that as `MAHANAVI_TELEGRAM_ADMIN_CHAT_ID`. (Bots can't message
   a chat that hasn't contacted them first — this step is why.)

### 5. Set up YouTube (required, and the one to slow down for)

The YouTube Data API has no endpoint for creating Community posts (true
as of when this was built — worth re-confirming, since Google does
occasionally expand API coverage). Because of that, publishing uses
Playwright browser automation instead, which means:

- Run the one-time login capture **before your first real run**:
  ```bash
  python -m mahanavi.scripts.youtube_login_setup
  ```
  This opens a real browser window — log in by hand, then press Enter in
  the terminal. It saves your session to
  `MAHANAVI_YOUTUBE_SESSION_STATE_FILE` for reuse. Re-run this whenever
  the session expires.
- **Read the docstring at the top of
  `publishers/youtube_playwright_uploader.py` before relying on this.**
  It automates your personal YouTube/Google account, which sits in a gray
  area of YouTube's Terms of Service around automated access — this can
  trigger security challenges or, rarely, account restrictions. That risk
  exists independent of how carefully the code is written.
- The CSS/role selectors in `publishers/youtube_selectors.py` are a
  best-effort template — Studio's UI changes without notice, and I had no
  way to browse it live while writing this. **Do a manual `--run-now`
  test and watch it happen** before trusting the unattended 5 AM schedule.
  On failure, it captures a screenshot to help you fix the selectors.

### 6. (Optional) Facebook and Instagram

Both use official Graph API endpoints (no browser automation needed).

- **Facebook**: create a Meta App, get a long-lived Page Access Token
  with `pages_manage_posts` + `pages_read_engagement`. Set
  `MAHANAVI_ENABLE_FACEBOOK=true` and the `FACEBOOK_*` variables.
- **Instagram**: same Meta App, an Instagram Business/Creator account
  linked to a Facebook Page. **Real API constraint**: Instagram's Graph
  API only accepts a *publicly reachable image URL* — not a file upload.
  You need to host `data/generated/` somewhere public (nginx, S3,
  Cloudflare R2, etc.) and set `MAHANAVI_INSTAGRAM_IMAGE_PUBLIC_BASE_URL`
  to that public base URL. Set `MAHANAVI_ENABLE_INSTAGRAM=true` and the
  `INSTAGRAM_*` variables.

### 7. (Optional) Real Panchang data

By default, `MAHANAVI_PANCHANG_PROVIDER=dummy` uses offline, deterministic
placeholder data — good for testing the pipeline, **not astronomically
accurate**, do not use it for real posts. To go live:

- **API**: set `MAHANAVI_PANCHANG_PROVIDER=api` and
  `MAHANAVI_PANCHANG_API_BASE_URL` (+ `_API_KEY` if needed). If your
  provider's JSON field names differ from what's expected, adjust
  `_FIELD_MAP` in `panchang/api_provider.py` — nothing else needs to change.
- **Scraper**: set `MAHANAVI_PANCHANG_PROVIDER=scraper` and construct
  `ScraperPanchangProvider` directly in `bootstrap.py` with your target
  site's URL template and CSS selectors (see the docstring in
  `panchang/scraper_provider.py`). Confirm scraping is permitted by that
  site's terms of service first.

## Configuration reference

Every setting lives in `.env` (copy from `.env.example`), all prefixed
`MAHANAVI_`. Full list and defaults are in `src/mahanavi/config.py`.
Key ones you'll actually touch:

| Variable | Purpose |
|---|---|
| `IMAGES_ROOT`, `OUTPUT_DIR`, `DATABASE_PATH`, `LOG_DIR` | Paths — defaults are fine for local dev |
| `TIMEZONE`, `POST_HOUR`, `POST_MINUTE` | When the scheduler posts |
| `CHANNEL_NAME`, `WATERMARK_TEXT`, `TELUGU_FONT_PATH`, `LOGO_PATH` | Branding |
| `PANCHANG_PROVIDER` | `dummy` / `api` / `scraper` |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID`, `TELEGRAM_ADMIN_CHAT_ID` | Telegram (posting + notifications) |
| `YOUTUBE_SESSION_STATE_FILE` | Where the login setup script saves your session |
| `ENABLE_FACEBOOK`, `ENABLE_INSTAGRAM` + their credentials | Optional extra platforms |
| `MAX_RETRIES`, `RETRY_BACKOFF_SECONDS` | Retry behavior for every network call |

## Running it

**Manual test run (recommended before trusting the schedule):**

```bash
python -m mahanavi.main --run-now
python -m mahanavi.main --run-now --date 2026-07-20   # test a specific date
```

Runs the full pipeline once and exits — the fastest way to see what
actually happens without waiting for 5 AM.

**Start the scheduler (runs forever):**

```bash
python -m mahanavi.main
```

## Testing

```bash
pip install pytest pytest-cov mypy
PYTHONPATH=src pytest                                       # full suite
PYTHONPATH=src pytest --cov=mahanavi --cov-report=term-missing
PYTHONPATH=src mypy src/mahanavi --ignore-missing-imports    # type checking
```

CI (`.github/workflows/ci.yml`) runs both automatically on every push/PR,
plus a job that builds the Docker image.

## Docker

```bash
docker compose up -d                                    # start the scheduler
docker compose run --rm app python -m mahanavi.main --run-now
docker compose logs -f
```

Run `scripts/youtube_login_setup.py` **outside Docker** first (it needs a
visible browser window), then make sure the saved session file lands in
the `data/` volume so the container can use it.

**Honest note:** the Dockerfile is carefully constructed (built on
Playwright's official base image specifically to avoid the usual
"chromium won't launch in prod" dependency problems) but was written in
an environment without Docker or network access to verify the build. The
`docker-build` CI job is the first real test of it — if it fails, start
there, and check that the base image tag still matches the `playwright`
version pinned in `requirements.txt`.

## Extending the system

- **New Panchang source**: implement `PanchangProvider` in `panchang/`,
  wire it into `panchang/factory.py`.
- **New publish target**: implement `Uploader` in `publishers/`, add it
  to `publishers/factory.py`.
- **New notification channel**: implement `Notifier`, swap it in
  `bootstrap.py`'s `_build_notifier`.
- **New deity/day**: add a folder under `Images/`, an entry to
  `WEEKDAY_FOLDER_MAP` in `config.py`, a `Deity` enum value in
  `core/models.py`, a Telugu name in `images/telugu_text.py`, and content
  in `content/data.py`.
- **LLM-generated captions instead of templates**: replace
  `TemplateContentGenerator` with a new `ContentGenerator` implementation
  — `DailyPipeline` only depends on the interface.

## Known limitations — read before relying on this daily

- **YouTube automation risk**: see the Setup section above. This is the
  single biggest operational risk in the system, not a code defect.
- **YouTube selectors need live verification**: Studio's UI changes
  without notice; the selectors here are a best-effort starting point.
- **Telugu content should get a native-speaker review**: the devotional
  phrasing in `content/data.py` follows standard conventions but wasn't
  written by a native Telugu speaker.
- **Trending hashtags are a static curated list**: real hashtag trends
  shift — revisit `TRENDING_DEVOTIONAL_HASHTAGS` periodically.
- **Instagram requires public image hosting** — it's a real API
  constraint, not something this codebase can work around.
- **Dummy Panchang data is not astronomically accurate** — fine for
  testing the pipeline, not for real posts.
- **Caption length limits are soft-configured**, not verified against
  each platform's *current* limit — confirm those before relying on the
  defaults, especially YouTube's Community Post caption limit.
