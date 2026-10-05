#!/usr/bin/env bash
# make-npc.sh — build a Hermes NPC Bot from a campaign dossier.
#
# Usage:   bash bot/npc-maker/make-npc.sh <campaign_id> <npc_slug> [--verify-only] [--soul-source <path>]
# Example: bash bot/npc-maker/make-npc.sh delta-green-convergence billy-ray-spivey
#
# Sources of truth (per NPC, under the gitignored campaign data layer):
#   campaigns/<campaign_id>/npcs/<npc_slug>/dossier.md   the answered character sheet
#   campaigns/<campaign_id>/npcs/<npc_slug>/soul.md      the bot's persona file (goes in as SOUL.md)
#   campaigns/<campaign_id>/npcs/<npc_slug>/bot.yaml     metadata: title / description / model / provider
#
# Result: an isolated Hermes profile  ~/.hermes/profiles/npc-<npc_slug>
#   - minimal config; same model stack as the GM (default deepseek-flash; one-line swap)
#   - SOUL.md + dossier.md copied into the profile
#   - Bot Mode marker in profile.yaml; canonical "Bot Chat" session created
#
# Model policy: NPCs run the same stack as the GM — default deepseek-flash on the
# deepseek provider (owner call 2026-10-04; supersedes free-OpenRouter-for-NPCs).
# bot.yaml may set `provider:` and `model:`; those defaults apply otherwise.
# Bind = model.default, set to the RAW model id (no alias): an alias value that
# starts with a provider-style vendor token (e.g. "qwen/") gets re-routed by the
# CLI's provider auto-detection to that vendor's own provider (verified 2026-10-04).
# Swap one line:  hermes -p npc-<slug> config set model.default <model-id>
#
# Notes:
#   - .env is written by script (never by hand): only the provider's key
#     (DEEPSEEK_API_KEY by default), with a timestamped backup. Values never print.
#   - Bot Mode needs (a) a session titled exactly "Bot Chat" and (b) a
#     `ui_meta: { hermes-bots: ... }` block in profile.yaml. This install already
#     carries the marker on the ttrpg profile, so one marked profile marks the install.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
GM_ENV="$HOME/.hermes/profiles/ttrpg/.env"

campaign="${1:-}"; slug="${2:-}"; shift 2 2>/dev/null || true
mode=""; soulsrc=""
while [ $# -gt 0 ]; do
  case "$1" in
    --verify-only) mode="--verify-only" ;;
    --soul-source) soulsrc="${2:-}"; shift ;;
    *) echo "unknown option: $1"; exit 2 ;;
  esac
  shift
done
if [ -z "$campaign" ] || [ -z "$slug" ]; then
  echo "usage: make-npc.sh <campaign_id> <npc_slug> [--verify-only] [--soul-source <path>]"; exit 2
fi

src="$REPO/campaigns/$campaign/npcs/$slug"
profile="npc-$slug"
home="$HOME/.hermes/profiles/$profile"
soulsrc="${soulsrc:-$src/soul.md}"

if [ "$mode" = "--verify-only" ]; then
  [ -f "$src/bot.yaml" ] || { echo "FATAL: missing $src/bot.yaml"; exit 1; }
else
  for f in dossier.md bot.yaml; do
    [ -f "$src/$f" ] || { echo "FATAL: missing $src/$f"; exit 1; }
  done
  [ -f "$soulsrc" ] || { echo "FATAL: missing SOUL source $soulsrc"; exit 1; }
fi

# --- metadata (single-line values; description folded to one line) ---
title="$(sed -n 's/^title: *//p' "$src/bot.yaml" | head -1)"
model="$(sed -n 's/^model: *//p' "$src/bot.yaml" | head -1)"
provider="$(sed -n 's/^provider: *//p' "$src/bot.yaml" | head -1)"
provider="${provider:-deepseek}"
desc="$(awk '/^description:/{f=1;sub(/^description: */,"");if($0==">"||$0=="|"||$0==">-"||$0=="|-")next;print;next} f&&/^[A-Za-z_][A-Za-z0-9_]*:/{f=0} f{print}' "$src/bot.yaml" | tr '\n' ' ' | sed 's/  */ /g;s/^ *//;s/ *$//')"
[ -n "$title" ] && [ -n "$model" ] || { echo "FATAL: bot.yaml needs title + model"; exit 1; }

echo "== NPC bot: $profile — \"$title\""
echo "   source: $src"
echo "   model:  $model (provider: $provider)"

if [ "$mode" != "--verify-only" ]; then
  # --- 1. profile skeleton (idempotent) ---
  if [ ! -d "$home" ]; then
    hermes profile create "$profile" --no-skills --description "$desc" 2>&1 | tail -3
  else
    echo "-- profile exists; refreshing content only"
  fi

  # --- 2. model + agent wiring ---
  hermes -p "$profile" config set model.provider "$provider" >/dev/null
  hermes -p "$profile" config set model.default "$model" >/dev/null
  hermes -p "$profile" config set agent.max_turns 10 >/dev/null
  hermes -p "$profile" config set agent.task_completion_guidance false >/dev/null
  hermes -p "$profile" config set memory.memory_enabled true >/dev/null
  hermes -p "$profile" config set memory.memory_char_limit 500 >/dev/null
  hermes -p "$profile" config set memory.user_char_limit 500 >/dev/null

  # --- 3. .env — the provider's key, scripted, with a backup ---
  case "$provider" in
    deepseek)   keyvar="DEEPSEEK_API_KEY" ;;
    openrouter) keyvar="OPENROUTER_API_KEY" ;;
    *)          keyvar="" ;;
  esac
  if [ -n "$keyvar" ] && ! grep -q "^$keyvar=." "$home/.env" 2>/dev/null; then
    cp "$home/.env" "$home/.env.bak-$(date +%Y%m%d-%H%M%S)"
    key="$(grep "^$keyvar=" "$GM_ENV" | head -1 | cut -d= -f2-)"
    [ -n "$key" ] || { echo "FATAL: $keyvar not found in $GM_ENV"; exit 1; }
    printf '\n# %s — NPC model credential (see bot/npc-maker/README.md)\n%s=%s\n' "$keyvar" "$keyvar" "$key" >> "$home/.env"
    unset key
  fi

  # --- 4. persona + dossier into the profile ---
  cp "$soulsrc" "$home/SOUL.md"
  cp "$src/dossier.md" "$home/dossier.md"

  # --- 5. Bot Mode marker (idempotent) ---
  if ! grep -q 'hermes-bots:' "$home/profile.yaml"; then
    python3 - "$home/profile.yaml" "$title" <<'PY'
import json, sys, time
path, title = sys.argv[1], sys.argv[2]
with open(path) as f:
    content = f.read()
if not content.endswith("\n"):
    content += "\n"
content += "ui_meta:\n  hermes-bots:\n    title: %s\n    created: %d\n" % (json.dumps(title), int(time.time() * 1000))
with open(path, "w") as f:
    f.write(content)
PY
  fi

  # --- 6. canonical Bot Chat (the forever-chat; the messaging protocol injects from here) ---
  # guard the spawn against this shell's ambient memory env so no other store is touched
  ( unset TDAI_DATA_DIR TDAI_LLM_API_KEY TDAI_GATEWAY_API_KEY TDAI_GATEWAY_CONFIG \
      TDAI_LLM_MODEL TDAI_LLM_BASE_URL MEMORY_TENCENTDB_LLM_BASE_URL MEMORY_TENCENTDB_LLM_MODEL 2>/dev/null || true
    hermes -p "$profile" chat -c "Bot Chat" --create-if-missing </dev/null >/dev/null 2>&1 || true )
fi

# --- 7. verify ---
echo "== verify =="
echo -n "model.default      : "; hermes -p "$profile" config get model.default 2>/dev/null
echo "env                : $(grep -o '^[A-Z_][A-Z0-9_]*=' "$home/.env" | sort -u | tr '\n' ' ')"
grep -q 'hermes-bots:' "$home/profile.yaml" && echo "profile.yaml       : Bot Mode marker present"
sqlite3 "$home/state.db" "SELECT 'bot chat           : '||id||' ('||message_count||' msgs)' FROM sessions WHERE title='Bot Chat' LIMIT 1;" 2>/dev/null || echo "bot chat           : (not created yet)"
echo "== done: $profile =="
