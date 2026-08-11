#!/usr/bin/env bash

set -u

ROOT="/home/nestor/dev/granja-luna-agent"
STATE_DIR="$ROOT/runtime/state/social-automation"
RESULT="$STATE_DIR/2026-08-11-share-brahmas-reel-to-story.json"
LAST_MESSAGE="$STATE_DIR/2026-08-11-share-brahmas-reel-to-story.last.json"
RUN_LOG="$STATE_DIR/2026-08-11-share-brahmas-reel-to-story.codex.jsonl"
LOCK="$STATE_DIR/2026-08-11-share-brahmas-reel-to-story.lock"
SCHEMA="$ROOT/scripts/social/share_reel_to_story_result.schema.json"
PROMPT="$ROOT/scripts/social/share_reel_to_story_2026-08-11.prompt.md"
CODEX="/home/nestor/.local/bin/codex"

mkdir -p "$STATE_DIR"

exec 9>"$LOCK"
if ! flock -n 9; then
  exit 0
fi

if [[ -f "$RESULT" ]] && jq -e '.status == "shared" or .status == "already_shared"' "$RESULT" >/dev/null 2>&1; then
  exit 0
fi

write_failure() {
  local reason="$1"
  jq -n \
    --arg status "failed" \
    --arg at "$(date --iso-8601=seconds)" \
    --arg details "$reason" \
    '{status: $status, executed_at: $at, page: "Granja Luna", reel_match: false, story_share: false, verification: false, details: $details, evidence: []}' \
    >"$RESULT"
}

notify_desktop() {
  local summary="$1"
  local body="$2"
  /usr/bin/gdbus call --session \
    --dest org.freedesktop.Notifications \
    --object-path /org/freedesktop/Notifications \
    --method org.freedesktop.Notifications.Notify \
    "Granja Luna" 0 "" "$summary" "$body" '[]' '{}' 10000 \
    >/dev/null 2>&1 || true
}

if ! curl --silent --fail http://127.0.0.1:9222/json/version >/dev/null; then
  write_failure "Chrome no estaba disponible en el puerto de depuración 9222. No se realizó ninguna acción en Facebook."
  notify_desktop "No se pudo compartir la historia" "Chrome no estaba disponible. Revisá el registro de Granja Luna."
  exit 1
fi

set +e
timeout 20m "$CODEX" \
  -a never \
  -s danger-full-access \
  exec \
  --ephemeral \
  -C "$ROOT" \
  -c 'model_reasoning_effort="medium"' \
  --output-schema "$SCHEMA" \
  --output-last-message "$LAST_MESSAGE" \
  --json \
  - <"$PROMPT" >"$RUN_LOG" 2>&1
codex_status=$?
set -e

if [[ -s "$LAST_MESSAGE" ]] && jq -e . "$LAST_MESSAGE" >/dev/null 2>&1; then
  jq --arg at "$(date --iso-8601=seconds)" '. + {executed_at: $at}' "$LAST_MESSAGE" >"$RESULT"
else
  write_failure "Codex terminó sin producir un resultado estructurado (código $codex_status). Revisar el log JSONL de la ejecución."
fi

status="$(jq -r '.status // "failed"' "$RESULT" 2>/dev/null)"
if [[ "$status" == "shared" || "$status" == "already_shared" ]]; then
  notify_desktop "Historia de Granja Luna verificada" "Resultado: $status. El detalle quedó registrado localmente."
  exit 0
fi

notify_desktop "No se pudo confirmar la historia" "No se repitió la acción. Revisá el registro de Granja Luna."
exit 1
