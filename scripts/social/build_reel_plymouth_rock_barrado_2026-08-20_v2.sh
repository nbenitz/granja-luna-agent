#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE_DIR="media/inbox/imports/2026/08/20/upload-3674c08efbd14da6"
SOURCE_HOOK="$SOURCE_DIR/020-efc53783-309433.mp4"
SOURCE_DETAIL="$SOURCE_DIR/026-733b3c96-309427.mp4"
SOURCE_LANDSCAPE="$SOURCE_DIR/018-59a0314b-309437.mp4"
SOURCE_GROUP="$SOURCE_DIR/043-2f0c893d-309355.mp4"
SOURCE_CLOSING="$SOURCE_DIR/036-f4155f63-309410.mp4"
SUBTITLES="media/selected/social-drafts/2026-08-20-reel-plymouth-rock-barrado-v2.ass"
OUTPUT="media/selected/social-drafts/2026-08-20-reel-plymouth-rock-barrado-v2.mp4"
COVER="media/selected/social-drafts/2026-08-20-reel-plymouth-rock-barrado-cover-v2.jpg"
RUNTIME_OUTPUT="runtime/state/content-studio/social-drafts/2026-08-20-reel-plymouth-rock-barrado-v2.mp4"

cd "$ROOT"
mkdir -p "$(dirname "$OUTPUT")" "$(dirname "$RUNTIME_OUTPUT")"

# Los cinco originales son verticales con rotación -90 en la matriz de visualización.
# FFmpeg normaliza esa orientación antes de escalar. Luego se preserva la proporción
# completa; el pad sólo actúa como resguardo y no recorta ni deforma la imagen.
ffmpeg -y -hide_banner -loglevel warning \
  -autorotate 1 -i "$SOURCE_HOOK" \
  -autorotate 1 -i "$SOURCE_DETAIL" \
  -autorotate 1 -i "$SOURCE_LANDSCAPE" \
  -autorotate 1 -i "$SOURCE_GROUP" \
  -autorotate 1 -i "$SOURCE_CLOSING" \
  -filter_complex "
    [0:v]trim=start=6:end=9,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30[v0];
    [1:v]trim=start=0:end=3.2,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30[v1];
    [2:v]trim=start=0.2:end=3.8,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30[v2];
    [3:v]trim=start=0.2:end=4.2,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30[v3];
    [4:v]trim=start=0:end=4,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30[v4];

    [v0][v1]xfade=transition=fade:duration=0.25:offset=2.75[v01];
    [v01][v2]xfade=transition=fade:duration=0.25:offset=5.70[v012];
    [v012][v3]xfade=transition=fade:duration=0.25:offset=9.05[v0123];
    [v0123][v4]xfade=transition=fade:duration=0.25:offset=12.80[basev];

    [0:a]atrim=start=6:end=9,asetpts=PTS-STARTPTS,aresample=48000[a0];
    [1:a]atrim=start=0:end=3.2,asetpts=PTS-STARTPTS,aresample=48000[a1];
    [2:a]atrim=start=0.2:end=3.8,asetpts=PTS-STARTPTS,aresample=48000[a2];
    [3:a]atrim=start=0.2:end=4.2,asetpts=PTS-STARTPTS,aresample=48000[a3];
    [4:a]atrim=start=0:end=4,asetpts=PTS-STARTPTS,aresample=48000[a4];
    [a0][a1]acrossfade=d=0.25:c1=tri:c2=tri[a01];
    [a01][a2]acrossfade=d=0.25:c1=tri:c2=tri[a012];
    [a012][a3]acrossfade=d=0.25:c1=tri:c2=tri[a0123];
    [a0123][a4]acrossfade=d=0.25:c1=tri:c2=tri,highpass=f=80,lowpass=f=12000,afftdn=nr=7:nf=-45,loudnorm=I=-25:LRA=7:TP=-2.5,afade=t=in:st=0:d=0.2,afade=t=out:st=16.3:d=0.5[aout];

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
