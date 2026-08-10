#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE="media/inbox/imports/2026/08/09/upload-a8cb17bcf4ee44ab/001-fb7bf7e6-302758.mp4"
SUBTITLES="media/selected/social-drafts/2026-08-09-reel-cierre-pollitos-v2.ass"
OUTPUT="media/selected/social-drafts/2026-08-09-reel-cierre-pollitos-v2.mp4"
IMAGE="granja-luna-agent:content-upload-test"

mkdir -p "$ROOT/media/selected/social-drafts"

docker run --rm \
  -v "$ROOT:/workspace" \
  -w /workspace \
  "$IMAGE" \
  ffmpeg -y -hide_banner -loglevel warning \
  -i "$SOURCE" \
  -filter_complex "
    [0:v]trim=start=0:end=5,setpts=PTS-STARTPTS,split=2[v0bg][v0fg];
    [v0bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=45:steps=2,eq=brightness=-0.10[bg0];
    [v0fg]crop=768:1080:576:0,scale=1080:1518:flags=lanczos[fg0];
    [bg0][fg0]overlay=0:201,setsar=1,fps=30[v0];
    [0:a]atrim=start=0:end=5,asetpts=PTS-STARTPTS[a0];

    [0:v]trim=start=20:end=25.5,setpts=PTS-STARTPTS,split=2[v1bg][v1fg];
    [v1bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=45:steps=2,eq=brightness=-0.10[bg1];
    [v1fg]crop=768:1080:576:0,scale=1080:1518:flags=lanczos[fg1];
    [bg1][fg1]overlay=0:201,setsar=1,fps=30[v1];
    [0:a]atrim=start=20:end=25.5,asetpts=PTS-STARTPTS[a1];

    [0:v]trim=start=46:end=53,setpts=PTS-STARTPTS,split=2[v2bg][v2fg];
    [v2bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=45:steps=2,eq=brightness=-0.10[bg2];
    [v2fg]crop=768:1080:576:0,scale=1080:1518:flags=lanczos[fg2];
    [bg2][fg2]overlay=0:201,setsar=1,fps=30[v2];
    [0:a]atrim=start=46:end=53,asetpts=PTS-STARTPTS[a2];

    [0:v]trim=start=68:end=72.8,setpts=PTS-STARTPTS,split=2[v3bg][v3fg];
    [v3bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=45:steps=2,eq=brightness=-0.10[bg3];
    [v3fg]crop=768:1080:576:0,scale=1080:1518:flags=lanczos[fg3];
    [bg3][fg3]overlay=0:201,setsar=1,fps=30[v3];
    [0:a]atrim=start=68:end=72.8,asetpts=PTS-STARTPTS[a3];

    [v0][v1]xfade=transition=fade:duration=0.3:offset=4.7[v01];
    [v01][v2]xfade=transition=fade:duration=0.3:offset=9.9[v012];
    [v012][v3]xfade=transition=fade:duration=0.3:offset=16.6[basev];
    [a0][a1]acrossfade=d=0.3:c1=tri:c2=tri[a01];
    [a01][a2]acrossfade=d=0.3:c1=tri:c2=tri[a012];
    [a012][a3]acrossfade=d=0.3:c1=tri:c2=tri[basea];

    [basev]subtitles='$SUBTITLES':fontsdir=/usr/share/fonts/truetype/dejavu[vout];
    [basea]loudnorm=I=-24:LRA=7:TP=-2[aout]
  " \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset medium -crf 18 -profile:v high -level 4.1 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart \
  "$OUTPUT"

printf '%s\n' "$ROOT/$OUTPUT"
