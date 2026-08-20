#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE_DIR="media/inbox/imports/2026/08/13/upload-71b7d672b7784071"
SOURCE_1="$SOURCE_DIR/001-542d392c-303849.mp4"
SOURCE_2="$SOURCE_DIR/002-6f0ad107-303847.mp4"
SOURCE_4="$SOURCE_DIR/004-fd791097-303848.mp4"
SOURCE_5="$SOURCE_DIR/005-44747567-303846.mp4"
SOURCE_6="$SOURCE_DIR/006-8b5f1786-303844.mp4"
SUBTITLES="media/selected/social-drafts/2026-08-13-reel-por-que-comen-arena-v1.ass"
OUTPUT="media/selected/social-drafts/2026-08-13-reel-por-que-comen-arena-v1.mp4"
RUNTIME_OUTPUT="runtime/state/content-studio/social-drafts/2026-08-13-reel-por-que-comen-arena-v1.mp4"

cd "$ROOT"
mkdir -p "$(dirname "$OUTPUT")" "$(dirname "$RUNTIME_OUTPUT")"

ffmpeg -y -hide_banner -loglevel warning \
  -i "$SOURCE_1" \
  -i "$SOURCE_4" \
  -i "$SOURCE_5" \
  -i "$SOURCE_2" \
  -i "$SOURCE_6" \
  -filter_complex "
    [0:v]trim=start=0.3:end=4.8,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v0];
    [1:v]trim=start=0:end=4.2,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v1];
    [2:v]trim=start=0:end=5,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v2];
    [3:v]trim=start=0:end=5,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v3];
    [4:v]trim=start=20:end=24.5,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v4];

    [v0][v1]xfade=transition=fade:duration=0.3:offset=4.2[v01];
    [v01][v2]xfade=transition=fade:duration=0.3:offset=8.1[v012];
    [v012][v3]xfade=transition=fade:duration=0.3:offset=12.8[v0123];
    [v0123][v4]xfade=transition=fade:duration=0.3:offset=17.5[basev];

    [2:a]atrim=start=0:end=22,asetpts=PTS-STARTPTS,highpass=f=80,lowpass=f=12000,afftdn=nr=8:nf=-45,loudnorm=I=-28:LRA=7:TP=-2,afade=t=in:st=0:d=0.25,afade=t=out:st=21.5:d=0.5[aout];
    [basev]subtitles='$SUBTITLES':fontsdir=/usr/share/fonts/truetype/dejavu[vout]
  " \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset medium -crf 18 -profile:v high -level 4.1 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart \
  "$OUTPUT"

cp "$OUTPUT" "$RUNTIME_OUTPUT"
printf '%s\n' "$ROOT/$OUTPUT" "$ROOT/$RUNTIME_OUTPUT"
