#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE_DIR="media/inbox/imports/2026/08/20/upload-3674c08efbd14da6"
SOURCE_HOOK="$SOURCE_DIR/037-706f10f9-309411.mp4"
SOURCE_DETAIL="$SOURCE_DIR/059-355c563e-309310.mp4"
SOURCE_LANDSCAPE="$SOURCE_DIR/018-59a0314b-309437.mp4"
SOURCE_GROUP="$SOURCE_DIR/043-2f0c893d-309355.mp4"
SOURCE_CLOSING="$SOURCE_DIR/054-fb155eb0-309344.mp4"
SUBTITLES="media/selected/social-drafts/2026-08-20-reel-plymouth-rock-barrado-v1.ass"
OUTPUT="media/selected/social-drafts/2026-08-20-reel-plymouth-rock-barrado-v1.mp4"
COVER="media/selected/social-drafts/2026-08-20-reel-plymouth-rock-barrado-cover-v1.jpg"
RUNTIME_OUTPUT="runtime/state/content-studio/social-drafts/2026-08-20-reel-plymouth-rock-barrado-v1.mp4"

cd "$ROOT"
mkdir -p "$(dirname "$OUTPUT")" "$(dirname "$RUNTIME_OUTPUT")"

ffmpeg -y -hide_banner -loglevel warning \
  -i "$SOURCE_HOOK" \
  -i "$SOURCE_DETAIL" \
  -i "$SOURCE_LANDSCAPE" \
  -i "$SOURCE_GROUP" \
  -i "$SOURCE_CLOSING" \
  -filter_complex "
    [0:v]trim=start=20.75:end=23.55,setpts=PTS-STARTPTS,crop=608:1080:656:0,scale=1080:1920:flags=lanczos,setsar=1,fps=30[v0];
    [1:v]trim=start=0:end=2.8,setpts=PTS-STARTPTS,crop=608:1080:656:0,scale=1080:1920:flags=lanczos,setsar=1,fps=30[v1];

    [2:v]trim=start=0.2:end=3.6,setpts=PTS-STARTPTS,split=2[v2bg][v2fg];
    [v2bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=42:steps=2,eq=brightness=-0.14[bg2];
    [v2fg]scale=1080:608:flags=lanczos[fg2];
    [bg2][fg2]overlay=0:656,setsar=1,fps=30[v2];

    [3:v]trim=start=0.3:end=4.3,setpts=PTS-STARTPTS,crop=608:1080:656:0,scale=1080:1920:flags=lanczos,setsar=1,fps=30[v3];

    [4:v]trim=start=19:end=23.5,setpts=PTS-STARTPTS,split=2[v4bg][v4fg];
    [v4bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=42:steps=2,eq=brightness=-0.14[bg4];
    [v4fg]scale=1080:608:flags=lanczos[fg4];
    [bg4][fg4]overlay=0:656,setsar=1,fps=30[v4];

    [v0][v1]xfade=transition=fade:duration=0.25:offset=2.55[v01];
    [v01][v2]xfade=transition=fade:duration=0.25:offset=5.10[v012];
    [v012][v3]xfade=transition=fade:duration=0.25:offset=8.25[v0123];
    [v0123][v4]xfade=transition=fade:duration=0.25:offset=12.00[basev];

    [0:a]atrim=start=20.75:end=23.55,asetpts=PTS-STARTPTS,aresample=48000[a0];
    [1:a]atrim=start=0:end=2.8,asetpts=PTS-STARTPTS,aresample=48000[a1];
    [2:a]atrim=start=0.2:end=3.6,asetpts=PTS-STARTPTS,aresample=48000[a2];
    [3:a]atrim=start=0.3:end=4.3,asetpts=PTS-STARTPTS,aresample=48000[a3];
    [4:a]atrim=start=19:end=23.5,asetpts=PTS-STARTPTS,aresample=48000[a4];
    [a0][a1]acrossfade=d=0.25:c1=tri:c2=tri[a01];
    [a01][a2]acrossfade=d=0.25:c1=tri:c2=tri[a012];
    [a012][a3]acrossfade=d=0.25:c1=tri:c2=tri[a0123];
    [a0123][a4]acrossfade=d=0.25:c1=tri:c2=tri,highpass=f=80,lowpass=f=12000,afftdn=nr=7:nf=-45,loudnorm=I=-25:LRA=7:TP=-2.5,afade=t=in:st=0:d=0.2,afade=t=out:st=16.0:d=0.5[aout];

    [basev]subtitles='$SUBTITLES':fontsdir=/usr/share/fonts/truetype/dejavu[vout]
  " \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset medium -crf 18 -profile:v high -level 4.1 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 \
  -map_metadata -1 -movflags +faststart \
  "$OUTPUT"

cp "$OUTPUT" "$RUNTIME_OUTPUT"
ffmpeg -y -hide_banner -loglevel warning -ss 0.8 -i "$OUTPUT" -frames:v 1 \
  -q:v 2 -map_metadata -1 -update 1 "$COVER"
sha256sum "$OUTPUT" "$RUNTIME_OUTPUT" "$COVER"
