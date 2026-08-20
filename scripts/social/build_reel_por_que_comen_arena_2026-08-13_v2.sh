#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE_DIR="media/inbox/imports/2026/08/13/upload-71b7d672b7784071"
SOURCE_GROUP="$SOURCE_DIR/005-44747567-303846.mp4"
SOURCE_RED="$SOURCE_DIR/001-542d392c-303849.mp4"
SOURCE_BLACK="$SOURCE_DIR/004-fd791097-303848.mp4"
SOURCE_ROOSTER="$SOURCE_DIR/007-69bf0c88-303841.mp4"
SUBTITLES="media/selected/social-drafts/2026-08-13-reel-por-que-comen-arena-v2.ass"
OUTPUT="media/selected/social-drafts/2026-08-13-reel-por-que-comen-arena-v2.mp4"
RUNTIME_OUTPUT="runtime/state/content-studio/social-drafts/2026-08-13-reel-por-que-comen-arena-v2.mp4"

cd "$ROOT"
mkdir -p "$(dirname "$OUTPUT")" "$(dirname "$RUNTIME_OUTPUT")"

ffmpeg -y -hide_banner -loglevel warning \
  -i "$SOURCE_GROUP" \
  -i "$SOURCE_RED" \
  -i "$SOURCE_BLACK" \
  -i "$SOURCE_ROOSTER" \
  -filter_complex "
    [0:v]trim=start=0:end=5,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v0];
    [1:v]trim=start=9:end=13.8,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v1];
    [2:v]trim=start=0:end=4.8,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v2];

    [3:v]trim=start=0:end=4.3,setpts=PTS-STARTPTS,crop=608:1080:250:0,scale=1080:1920:flags=lanczos,setsar=1,fps=30[v3];

    [v0][v1]xfade=transition=fade:duration=0.3:offset=4.7[v01];
    [v01][v2]xfade=transition=fade:duration=0.3:offset=9.2[v012];
    [v012][v3]xfade=transition=fade:duration=0.3:offset=13.7[basev];

    [0:a]atrim=start=0:end=18,asetpts=PTS-STARTPTS,highpass=f=80,lowpass=f=12000,afftdn=nr=8:nf=-45,loudnorm=I=-28:LRA=7:TP=-2,afade=t=in:st=0:d=0.25,afade=t=out:st=17.5:d=0.5[aout];
    [basev]subtitles='$SUBTITLES':fontsdir=/usr/share/fonts/truetype/dejavu[vout]
  " \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset medium -crf 18 -profile:v high -level 4.1 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart \
  "$OUTPUT"

cp "$OUTPUT" "$RUNTIME_OUTPUT"
printf '%s\n' "$ROOT/$OUTPUT" "$ROOT/$RUNTIME_OUTPUT"
