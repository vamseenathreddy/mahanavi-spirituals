#!/usr/bin/env bash
# Retrying apt install for CI. A single hung "apt-get update" once stalled a Daily Shorts run for 90
# minutes (2026-10-07), which held the concurrency lock and made the night's last Short miss its window.
# Each attempt is time-boxed, so a hang costs minutes, not the whole run.
# 2026-10-23: the runner's default mirror (azure.archive.ubuntu.com) was slow several times in one day and failed
# runs at this step. From the 2nd attempt on, switch to the official archive.ubuntu.com mirror and force IPv4.
set -u
for attempt in 1 2 3 4; do
  if [ "$attempt" -ge 2 ]; then
    for f in /etc/apt/sources.list /etc/apt/sources.list.d/*.sources /etc/apt/sources.list.d/*.list; do
      [ -f "$f" ] && sudo sed -i 's#http://azure.archive.ubuntu.com#http://archive.ubuntu.com#g' "$f"
    done
  fi
  if sudo timeout 150 apt-get update -y -o Acquire::Retries=3 -o Acquire::http::Timeout=20 -o Acquire::ForceIPv4=true \
     && sudo timeout 300 apt-get install -y --no-install-recommends -o Acquire::ForceIPv4=true "$@"; then
    exit 0
  fi
  echo "apt attempt $attempt failed or timed out; retrying" >&2
  sleep 10
done
exit 1
