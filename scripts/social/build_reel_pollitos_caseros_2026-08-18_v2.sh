#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE_VIDEO="media/inbox/imports/2026/08/18/upload-ba4158529b3b460b/001-65c47e2d-310978.mp4"
SOURCE_OLDER="media/selected/social-drafts/2026-08-17-pollitos-caseros-vista-interior-vertical.jpg"
SUBTITLES="media/selected/social-drafts/2026-08-18-reel-pollitos-caseros-disponibilidad-v2.ass"
OUTPUT="media/selected/social-drafts/2026-08-18-reel-pollitos-caseros-disponibilidad-v2.mp4"
COVER="media/selected/social-drafts/2026-08-18-reel-pollitos-caseros-cover-v2.jpg"
RUNTIME_OUTPUT="runtime/state/content-studio/social-drafts/2026-08-18-reel-pollitos-caseros-disponibilidad-v2.mp4"

cd "$ROOT"
mkdir -p "$(dirname "$OUTPUT")" "$(dirname "$RUNTIME_OUTPUT")"

ffmpeg -y -hide_banner -loglevel warning \
  -i "$SOURCE_VIDEO" \
  -loop 1 -t 4 -i "$SOURCE_OLDER" \
  -filter_complex "
    [0:v]trim=start=1.2:end=4.7,setpts=PTS-STARTPTS,split=2[v0bg][v0fg];
    [v0bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=42:steps=2,eq=brightness=-0.16[bg0];
    [v0fg]scale=1080:608:flags=lanczos[fg0];
    [bg0][fg0]overlay=0:656,setsar=1,fps=30[v0];

    [0:v]trim=start=23.0:end=26.5,setpts=PTS-STARTPTS,split=2[v1bg][v1fg];
    [v1bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=42:steps=2,eq=brightness=-0.16[bg1];
    [v1fg]scale=1080:608:flags=lanczos[fg1];
    [bg1][fg1]overlay=0:656,setsar=1,fps=30[v1];

    [0:v]trim=start=92.5:end=96.5,setpts=PTS-STARTPTS,split=2[v2bg][v2fg];
    [v2bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=42:steps=2,eq=brightness=-0.16[bg2];
    [v2fg]scale=1080:608:flags=lanczos[fg2];
    [bg2][fg2]overlay=0:656,setsar=1,fps=30[v2];

    [1:v]scale=1080:1920:flags=lanczos,zoompan=z='min(zoom+0.00035,1.045)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,setsar=1[v3];

    [v0][v1]xfade=transition=fade:duration=0.25:offset=3.25[v01];
    [v01][v2]xfade=transition=fade:duration=0.25:offset=6.50[v012];
    [v012][v3]xfade=transition=fade:duration=0.25:offset=10.25[basev];

    [0:a]atrim=start=1.2:end=4.7,asetpts=PTS-STARTPTS,aresample=48000[a0];
    [0:a]atrim=start=23.0:end=26.5,asetpts=PTS-STARTPTS,aresample=48000[a1];
    [0:a]atrim=start=92.5:end=96.5,asetpts=PTS-STARTPTS,aresample=48000[a2];
    anullsrc=r=48000:cl=stereo,atrim=duration=4.0[asilent];
    [a0][a1]acrossfade=d=0.25:c1=tri:c2=tri[a01];
    [a01][a2]acrossfade=d=0.25:c1=tri:c2=tri[a012];
    [a012][asilent]acrossfade=d=0.25:c1=tri:c2=tri,highpass=f=80,lowpass=f=12000,afftdn=nr=7:nf=-45,loudnorm=I=-25:LRA=7:TP=-2.5,afade=t=in:st=0:d=0.2,afade=t=out:st=13.7:d=0.5[aout];

    [basev]subtitles='$SUBTITLES':fontsdir=/usr/share/fonts/truetype/dejavu[vout]
  " \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset medium -crf 18 -profile:v high -level 4.1 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 \
  -map_metadata -1 -movflags +faststart \
  "$OUTPUT"

cp "$OUTPUT" "$RUNTIME_OUTPUT"
ffmpeg -y -hide_banner -loglevel warning -ss 1.5 -i "$OUTPUT" -frames:v 1 \
  -q:v 2 -map_metadata -1 -update 1 "$COVER"
sha256sum "$OUTPUT" "$RUNTIME_OUTPUT" "$COVER"
