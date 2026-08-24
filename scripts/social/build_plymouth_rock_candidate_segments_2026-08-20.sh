#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE_DIR="media/inbox/imports/2026/08/20/upload-3674c08efbd14da6"
OUTPUT_DIR="media/selected/social-drafts/segments/2026-08-20-plymouth-rock"
RUNTIME_DIR="runtime/state/content-studio/social-drafts/segments/2026-08-20-plymouth-rock"

cd "$ROOT"
mkdir -p "$OUTPUT_DIR" "$RUNTIME_DIR"

encode_vertical() {
  local source="$1"
  local start="$2"
  local duration="$3"
  local output="$4"

  ffmpeg -y -hide_banner -loglevel warning \
    -ss "$start" -t "$duration" -autorotate 1 -i "$source" \
    -vf "scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30" \
    -map 0:v:0 -map 0:a:0 \
    -c:v libx264 -preset medium -crf 18 -profile:v high -level 4.1 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -ar 48000 -map_metadata -1 -movflags +faststart \
    "$output"
}

encode_landscape_fit() {
  local source="$1"
  local start="$2"
  local duration="$3"
  local output="$4"

  ffmpeg -y -hide_banner -loglevel warning \
    -ss "$start" -t "$duration" -autorotate 1 -i "$source" \
    -filter_complex "
      [0:v]split=2[bg][fg];
      [bg]scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,gblur=sigma=42:steps=2,eq=brightness=-0.16[bgv];
      [fg]scale=1080:608:force_original_aspect_ratio=decrease:flags=lanczos,pad=1080:608:(ow-iw)/2:(oh-ih)/2:black[fgv];
      [bgv][fgv]overlay=0:656,setsar=1,fps=30[v]
    " \
    -map "[v]" -map 0:a:0 \
    -c:v libx264 -preset medium -crf 18 -profile:v high -level 4.1 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -ar 48000 -map_metadata -1 -movflags +faststart \
    "$output"
}

encode_vertical \
  "$SOURCE_DIR/018-59a0314b-309437.mp4" 0.2 3.6 \
  "$OUTPUT_DIR/2026-08-20-plymouth-rock-segment-018-landscape.mp4"

encode_landscape_fit \
  "$SOURCE_DIR/059-355c563e-309310.mp4" 0 4.2 \
  "$OUTPUT_DIR/2026-08-20-plymouth-rock-segment-059-individual.mp4"

encode_landscape_fit \
  "$SOURCE_DIR/037-706f10f9-309411.mp4" 22 2 \
  "$OUTPUT_DIR/2026-08-20-plymouth-rock-segment-037-close-22s.mp4"

encode_vertical \
  "$SOURCE_DIR/055-d4a33bd6-309345.mp4" 2 7 \
  "$OUTPUT_DIR/2026-08-20-plymouth-rock-segment-055-group-2s-9s.mp4"

encode_vertical \
  "$SOURCE_DIR/056-801ac75b-309346.mp4" 2 3.2 \
  "$OUTPUT_DIR/2026-08-20-plymouth-rock-segment-056-group-movement.mp4"

# Este tramo recupera el gesto de picotear la hoja junto a la columna que gustó en la V1.
encode_vertical \
  "$SOURCE_DIR/020-efc53783-309433.mp4" 7 2 \
  "$OUTPUT_DIR/2026-08-20-plymouth-rock-segment-020-leaf-near-post.mp4"

# Se conserva en el banco como antecedente, pero 036 queda fuera de la próxima versión.
encode_vertical \
  "$SOURCE_DIR/036-f4155f63-309410.mp4" 0 4 \
  "$OUTPUT_DIR/2026-08-20-plymouth-rock-segment-036-closing.mp4"

cp "$OUTPUT_DIR"/*.mp4 "$RUNTIME_DIR/"
sha256sum "$OUTPUT_DIR"/*.mp4
