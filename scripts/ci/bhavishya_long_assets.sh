#!/usr/bin/env bash
# Fetch the Bhavishya Purana long video and thumbnail from the assets branch into build/bhavishya/.
set -euo pipefail
git fetch --depth 1 origin assets-bhavishya
mkdir -p build
git archive FETCH_HEAD bhavishya | tar -x -C build
ls -la build/bhavishya
