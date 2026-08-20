#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE_PORTRAIT="media/inbox/Granja Luna/2026-08-15_pollitos-caseros_vista-general-interior_google-photos.mp4"
SOURCE_LANDSCAPE="media/inbox/Granja Luna/2026-08-03_pollitos-caseros_interior-criadero_google-photos.mp4"
SUBTITLES="media/selected/social-drafts/2026-08-17-reel-pollitos-caseros-disponibilidad-v1.ass"
OUTPUT="media/selected/social-drafts/2026-08-17-reel-pollitos-caseros-disponibilidad-v1.mp4"
RUNTIME_OUTPUT="runtime/state/content-studio/social-drafts/2026-08-17-reel-pollitos-caseros-disponibilidad-v1.mp4"

cd "$ROOT"
mkdir -p "$(dirname "$OUTPUT")" "$(dirname "$RUNTIME_OUTPUT")"

ffmpeg -y -hide_banner -loglevel warning \
  -i "$SOURCE_PORTRAIT" \
  -i "$SOURCE_LANDSCAPE" \
  -filter_complex "
    [0:v]trim=start=0:end=3.75,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v0];

    [1:v]trim=start=0.4:end=12.1,setpts=PTS-STARTPTS,split=2[v1bg][v1fg];
    [v1bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=42:steps=2,eq=brightness=-0.16[bg1];
    [v1fg]scale=1080:608:flags=lanczos[fg1];
    [bg1][fg1]overlay=0:656,setsar=1,fps=30[v1];

    [v0][v1]xfade=transition=fade:duration=0.25:offset=3.50[basev];

    [0:a]atrim=start=0:end=3.75,asetpts=PTS-STARTPTS,aresample=48000[a0];
    [1:a]atrim=start=0.4:end=12.1,asetpts=PTS-STARTPTS,aresample=48000[a1];
    [a0][a1]acrossfade=d=0.25:c1=tri:c2=tri,highpass=f=80,lowpass=f=12000,afftdn=nr=7:nf=-45,loudnorm=I=-25:LRA=7:TP=-2.5,afade=t=in:st=0:d=0.2,afade=t=out:st=14.7:d=0.5[aout];

    [basev]subtitles='$SUBTITLES':fontsdir=/usr/share/fonts/truetype/dejavu[vout]
  " \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset medium -crf 18 -profile:v high -level 4.1 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 \
  -map_metadata -1 -movflags +faststart \
  "$OUTPUT"

cp "$OUTPUT" "$RUNTIME_OUTPUT"
sha256sum "$OUTPUT" "$RUNTIME_OUTPUT"
