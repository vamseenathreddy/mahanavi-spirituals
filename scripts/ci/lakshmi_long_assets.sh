#!/usr/bin/env bash
# Fetch the Lakshmi long video (split in parts) and its thumbnail from the assets branch into build/lakshmi/.
set -euo pipefail
git fetch --depth 1 origin assets-lakshmi-long
mkdir -p build
git archive FETCH_HEAD lakshmi | tar -x -C build
cat build/lakshmi/long.mp4.part* > build/lakshmi/long.mp4
ls -la build/lakshmi
