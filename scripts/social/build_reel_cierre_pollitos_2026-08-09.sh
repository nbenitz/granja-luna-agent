#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE="media/inbox/imports/2026/08/09/upload-a8cb17bcf4ee44ab/001-fb7bf7e6-302758.mp4"
SUBTITLES="media/selected/social-drafts/2026-08-09-reel-cierre-pollitos-v1.ass"
OUTPUT="media/selected/social-drafts/2026-08-09-reel-cierre-pollitos-v1.mp4"
IMAGE="granja-luna-agent:content-upload-test"

mkdir -p "$ROOT/media/selected/social-drafts"

docker run --rm \
  -v "$ROOT:/workspace" \
  -w /workspace \
  "$IMAGE" \
  ffmpeg -y -hide_banner -loglevel warning \
  -i "$SOURCE" \
  -filter_complex "
    [0:v]trim=start=0:end=5,setpts=PTS-STARTPTS,crop=608:1080:656:0,scale=1080:1920:flags=lanczos,fps=30,setsar=1[v0];
    [0:a]atrim=start=0:end=5,asetpts=PTS-STARTPTS[a0];
    [0:v]trim=start=20:end=25.5,setpts=PTS-STARTPTS,crop=608:1080:656:0,scale=1080:1920:flags=lanczos,fps=30,setsar=1[v1];
    [0:a]atrim=start=20:end=25.5,asetpts=PTS-STARTPTS[a1];
    [0:v]trim=start=45:end=51,setpts=PTS-STARTPTS,crop=608:1080:656:0,scale=1080:1920:flags=lanczos,fps=30,setsar=1[v2];
    [0:a]atrim=start=45:end=51,asetpts=PTS-STARTPTS[a2];
    [0:v]trim=start=62.5:end=70,setpts=PTS-STARTPTS,crop=608:1080:656:0,scale=1080:1920:flags=lanczos,fps=30,setsar=1[v3];
    [0:a]atrim=start=62.5:end=70,asetpts=PTS-STARTPTS[a3];
    [v0][a0][v1][a1][v2][a2][v3][a3]concat=n=4:v=1:a=1[basev][basea];
    [basev]subtitles='$SUBTITLES':fontsdir=/usr/share/fonts/truetype/dejavu[vout];
    [basea]loudnorm=I=-24:LRA=7:TP=-2[aout]
  " \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset medium -crf 18 -profile:v high -level 4.1 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart \
  "$OUTPUT"

printf '%s\n' "$ROOT/$OUTPUT"
