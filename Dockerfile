# Playwright's official base image bundles Chromium plus every system
# library it needs, already tested together. Hand-rolling that apt package
# list yourself (libnss3, libatk-bridge2.0-0, libgtk-3-0, ... — a few dozen
# packages) is a common source of "chromium fails to launch" errors that
# only show up in production, so we deliberately don't do that here.
#
# TWO THINGS TO VERIFY BEFORE RELYING ON THIS IN PRODUCTION:
#   1. The tag below should match the `playwright` version pinned in
#      requirements.txt as closely as possible — a mismatched browser
#      binary vs. Python package version is a real source of failures.
#      Check https://mcr.microsoft.com/en-us/product/playwright/python/tags
#      for the current tag before building.
#   2. This image's Python version follows Playwright's own release
#      schedule and may not be exactly Python 3.13 (this project's target).
#      Run `docker run --rm <image> python3 --version` after building and
#      adjust if it matters for your workflow.
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

# Install Python dependencies first — this layer only rebuilds when
# requirements.txt changes, not on every source code edit.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code, bundled assets (Telugu font, logo), and package config.
COPY src/ ./src/
COPY assets/ ./assets/
COPY pyproject.toml .

# Runtime data (SQLite DB, logs, generated images, saved YouTube session)
# persists here — mount a host directory or named volume over this path.
VOLUME ["/app/data"]

# Your actual devotional images live outside the image — mount them at
# runtime, e.g.: docker run -v /path/to/your/Images:/app/Images ...
VOLUME ["/app/Images"]

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Default: start the scheduler (runs forever, posts daily at the configured
# time). For a one-off manual test instead, override the command:
#   docker run <image> python -m mahanavi.main --run-now
ENTRYPOINT ["python", "-m", "mahanavi.main"]
