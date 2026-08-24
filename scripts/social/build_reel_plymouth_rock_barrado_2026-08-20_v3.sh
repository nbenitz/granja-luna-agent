#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SEGMENT_DIR="media/selected/social-drafts/segments/2026-08-20-plymouth-rock"
SOURCE_HOOK="$SEGMENT_DIR/2026-08-20-plymouth-rock-segment-018-landscape.mp4"
SOURCE_DETAIL="$SEGMENT_DIR/2026-08-20-plymouth-rock-segment-059-individual.mp4"
SOURCE_BEHAVIOR="$SEGMENT_DIR/2026-08-20-plymouth-rock-segment-020-leaf-near-post.mp4"
SOURCE_CLOSE="$SEGMENT_DIR/2026-08-20-plymouth-rock-segment-037-close-22s.mp4"
SOURCE_GROUP="$SEGMENT_DIR/2026-08-20-plymouth-rock-segment-055-group-2s-9s.mp4"
SOURCE_CLOSING="$SEGMENT_DIR/2026-08-20-plymouth-rock-segment-056-group-movement.mp4"
SUBTITLES="media/selected/social-drafts/2026-08-20-reel-plymouth-rock-barrado-v3.ass"
OUTPUT="media/selected/social-drafts/2026-08-20-reel-plymouth-rock-barrado-v3.mp4"
COVER="media/selected/social-drafts/2026-08-20-reel-plymouth-rock-barrado-cover-v3.jpg"
RUNTIME_OUTPUT="runtime/state/content-studio/social-drafts/2026-08-20-reel-plymouth-rock-barrado-v3.mp4"

cd "$ROOT"
mkdir -p "$(dirname "$OUTPUT")" "$(dirname "$RUNTIME_OUTPUT")"

ffmpeg -y -hide_banner -loglevel warning \
  -i "$SOURCE_HOOK" \
  -i "$SOURCE_DETAIL" \
  -i "$SOURCE_BEHAVIOR" \
  -i "$SOURCE_CLOSE" \
  -i "$SOURCE_GROUP" \
  -i "$SOURCE_CLOSING" \
  -filter_complex "
    [0:v]trim=start=0:end=3.6,setpts=PTS-STARTPTS,setsar=1,fps=30[v0];
    [1:v]trim=start=0:end=4.2,setpts=PTS-STARTPTS,setsar=1,fps=30[v1];
    [2:v]trim=start=0:end=2,setpts=PTS-STARTPTS,setsar=1,fps=30[v2];
    [3:v]trim=start=0:end=2,setpts=PTS-STARTPTS,setsar=1,fps=30[v3];
    [4:v]trim=start=0:end=7,setpts=PTS-STARTPTS,setsar=1,fps=30[v4];
    [5:v]trim=start=0:end=3.2,setpts=PTS-STARTPTS,setsar=1,fps=30[v5];

    [v0][v1]xfade=transition=fade:duration=0.25:offset=3.35[v01];
    [v01][v2]xfade=transition=fade:duration=0.25:offset=7.30[v012];
    [v012][v3]xfade=transition=fade:duration=0.25:offset=9.05[v0123];
    [v0123][v4]xfade=transition=fade:duration=0.25:offset=10.80[v01234];
    [v01234][v5]xfade=transition=fade:duration=0.25:offset=17.55[basev];

    [0:a]atrim=start=0:end=3.6,asetpts=PTS-STARTPTS,aresample=48000[a0];
    [1:a]atrim=start=0:end=4.2,asetpts=PTS-STARTPTS,aresample=48000[a1];
    [2:a]atrim=start=0:end=2,asetpts=PTS-STARTPTS,aresample=48000[a2];
    [3:a]atrim=start=0:end=2,asetpts=PTS-STARTPTS,aresample=48000[a3];
    [4:a]atrim=start=0:end=7,asetpts=PTS-STARTPTS,aresample=48000[a4];
    [5:a]atrim=start=0:end=3.2,asetpts=PTS-STARTPTS,aresample=48000[a5];
    [a0][a1]acrossfade=d=0.25:c1=tri:c2=tri[a01];
    [a01][a2]acrossfade=d=0.25:c1=tri:c2=tri[a012];
    [a012][a3]acrossfade=d=0.25:c1=tri:c2=tri[a0123];
    [a0123][a4]acrossfade=d=0.25:c1=tri:c2=tri[a01234];
    [a01234][a5]acrossfade=d=0.25:c1=tri:c2=tri,highpass=f=80,lowpass=f=12000,afftdn=nr=7:nf=-45,loudnorm=I=-25:LRA=7:TP=-2.5,afade=t=in:st=0:d=0.2,afade=t=out:st=20.25:d=0.5[aout];

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
