#!/usr/bin/env bash
# repin-model.sh — re-pin an NPC bot's sessions to the profile's current model stack.
#
# Why this exists: sessions remember their model. A model swap updates the profile
# config, but every existing session row keeps the OLD model as its stored pin —
# resumed turns then restore the old model and (for the canonical Bot Chat) the
# session's stored system prompt keeps the old identity until rebuilt. The CLI's
# restore line reports the PIN; only a live turn + the bot's own logs/agent.log
# ("conversation turn: … model=") reports what actually ran. This script updates
# the pin safely and proves the effective model with one live turn.
#
# Usage:
#   bash bot/npc-maker/repin-model.sh <npc_slug> [--model <raw-id>] [--provider <name>] \
#                                                  [--base-url <url>] [--offline]
#
# Defaults: model/provider are read from the profile config (model.default /
# model.provider). base_url resolution order: --base-url → the GM profile's most
# recent session on the same provider (known-good same-stack source) → built-in
# map for deepseek/openrouter → error. --offline skips the live verification turn
# (readback only — NOT proof; flagged as such).
#
# Keep bot.yaml in sync so future maker rebuilds don't regress:
#   campaigns/<campaign_id>/npcs/<npc_slug>/bot.yaml  →  model: / provider:
set -euo pipefail

slug="${1:-}"; shift || true
[ -n "$slug" ] || { echo "usage: repin-model.sh <npc_slug> [--model <id>] [--provider <name>] [--base-url <url>] [--offline]"; exit 2; }
slug="${slug#npc-}"
profile="npc-$slug"
home="$HOME/.hermes/profiles/$profile"
db="$home/state.db"
[ -f "$db" ] || { echo "FATAL: no state.db for profile $profile ($db)"; exit 1; }

model=""; provider=""; base_url=""; offline=0
while [ $# -gt 0 ]; do
  case "$1" in
    --model)    model="${2:-}"; shift ;;
    --provider) provider="${2:-}"; shift ;;
    --base-url) base_url="${2:-}"; shift ;;
    --offline)  offline=1 ;;
    *) echo "unknown option: $1"; exit 2 ;;
  esac
  shift
done

model="${model:-$(hermes -p "$profile" config get model.default 2>/dev/null || true)}"
provider="${provider:-$(hermes -p "$profile" config get model.provider 2>/dev/null || true)}"
[ -n "$model" ] && [ -n "$provider" ] || { echo "FATAL: could not resolve model/provider (pass --model/--provider)"; exit 1; }

if [ -z "$base_url" ]; then
  base_url="$(sqlite3 "$HOME/.hermes/profiles/ttrpg/state.db" \
    "SELECT billing_base_url FROM sessions WHERE billing_provider='$provider' AND billing_base_url IS NOT NULL AND billing_base_url!='' ORDER BY COALESCE(last_activity_at,started_at) DESC LIMIT 1;" 2>/dev/null || true)"
fi
if [ -z "$base_url" ]; then
  case "$provider" in
    deepseek)   base_url="https://api.deepseek.com/v1" ;;
    openrouter) base_url="https://openrouter.ai/api/v1" ;;
  esac
fi
[ -n "$base_url" ] || { echo "FATAL: cannot infer base_url for provider '$provider' — pass --base-url"; exit 1; }

echo "== repin: $profile → model=$model provider=$provider base_url=$base_url"
echo "-- pins before:"
sqlite3 "$db" "SELECT id||' | '||COALESCE(title,'')||' | '||COALESCE(model,'(null)')||' | '||COALESCE(billing_provider,'(null)')||' | '||COALESCE(billing_base_url,'(null)') FROM sessions;"

bak="$db.bak-repin-$(date +%Y%m%d-%H%M%S)"
sqlite3 "$db" ".backup '$bak'"
echo "-- backup: $bak"

changed="$(sqlite3 "$db" "UPDATE sessions SET model='$model', billing_provider='$provider', billing_base_url='$base_url' WHERE COALESCE(model,'')!='$model' OR COALESCE(billing_provider,'')!='$provider' OR COALESCE(billing_base_url,'')!='$base_url'; SELECT changes();")"
echo "-- session rows updated: $changed"
echo "-- pins after:"
sqlite3 "$db" "SELECT id||' | '||COALESCE(title,'')||' | '||COALESCE(model,'')||' | '||COALESCE(billing_provider,'')||' | '||COALESCE(billing_base_url,'') FROM sessions;"

if [ "$offline" = "1" ]; then
  echo "-- offline mode: skipping the live verification turn (readback is readback, not proof)."
  exit 0
fi

echo "== live verification (one resumed turn into the Bot Chat) =="
qfile="$(mktemp -t npc-repin.XXXXXX)"
printf 'Voice check — one short line in character, no plot, nothing else.' > "$qfile"
( unset TDAI_DATA_DIR TDAI_LLM_API_KEY TDAI_GATEWAY_API_KEY TDAI_GATEWAY_CONFIG \
    TDAI_LLM_MODEL TDAI_LLM_BASE_URL MEMORY_TENCENTDB_LLM_BASE_URL MEMORY_TENCENTDB_LLM_MODEL 2>/dev/null || true
  mkdir -p "$home/workspace"; cd "$home/workspace"
  hermes -p "$profile" chat -c "Bot Chat" -Q --query-file "$qfile" 2>&1 ) | sed '/^session_id:/d' | tail -n 12
rm -f "$qfile"
logline="$(grep 'conversation turn' "$home/logs/agent.log" 2>/dev/null | tail -1 || true)"
if [ -n "$logline" ]; then
  echo "-- agent.log: $logline"
else
  echo "-- agent.log: WARN — no conversation-turn line found"
fi
case "$logline" in
  *"model=$model"*) echo "== PASS: the live turn ran on $model" ;;
  *)                echo "== CHECK: agent.log does not show model=$model — inspect manually before trusting the pin" ;;
esac
