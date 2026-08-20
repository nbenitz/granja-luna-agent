#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
IMPORT_DIR="media/inbox/imports/2026/08/18/upload-ba4158529b3b460b"
OUTPUT_DIR="media/selected/social-drafts"

cd "$ROOT"
mkdir -p "$OUTPUT_DIR"

ffmpeg -y -hide_banner -loglevel warning -autorotate 1 \
  -i "$IMPORT_DIR/004-09eb2c8b-310976.jpg" -frames:v 1 -q:v 2 -map_metadata -1 -update 1 \
  "$OUTPUT_DIR/2026-08-18-facebook-pollitos-caseros-1-semana-01.jpg"

ffmpeg -y -hide_banner -loglevel warning -autorotate 1 \
  -i "$IMPORT_DIR/003-d01184db-310977.jpg" -frames:v 1 -q:v 2 -map_metadata -1 -update 1 \
  "$OUTPUT_DIR/2026-08-18-facebook-pollitos-caseros-1-semana-02.jpg"

ffmpeg -y -hide_banner -loglevel warning -autorotate 1 \
  -i "$IMPORT_DIR/002-724f8bf5-310979.jpg" -frames:v 1 -q:v 2 -map_metadata -1 -update 1 \
  "$OUTPUT_DIR/2026-08-18-facebook-pollitos-caseros-1-semana-03.jpg"

ffmpeg -y -hide_banner -loglevel warning \
  -i "$OUTPUT_DIR/2026-08-17-pollitos-caseros-vista-interior-vertical.jpg" \
  -frames:v 1 -q:v 2 -map_metadata -1 -update 1 \
  "$OUTPUT_DIR/2026-08-18-facebook-pollitos-caseros-4-a-6-semanas-04.jpg"

sha256sum \
  "$OUTPUT_DIR/2026-08-18-facebook-pollitos-caseros-1-semana-01.jpg" \
  "$OUTPUT_DIR/2026-08-18-facebook-pollitos-caseros-1-semana-02.jpg" \
  "$OUTPUT_DIR/2026-08-18-facebook-pollitos-caseros-1-semana-03.jpg" \
  "$OUTPUT_DIR/2026-08-18-facebook-pollitos-caseros-4-a-6-semanas-04.jpg"
