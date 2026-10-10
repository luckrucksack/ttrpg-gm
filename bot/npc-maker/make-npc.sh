#!/usr/bin/env bash
# make-npc.sh — build or refresh a Hermes NPC Bot from campaign files. (base structure v2)
#
# Usage:   bash bot/npc-maker/make-npc.sh <campaign_id> <npc_slug> [--verify-only] [--smoke] [--soul-source <path>]
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
#   - v2: neutral working directory pinned (terminal.cwd) so no operator context
#     (AGENTS.md / git snapshots from the repo or launch dir) ever loads into a
#     character prompt — knowledge boundaries are a filesystem fact
#   - v2: tools policy — every toolset except `memory` is disabled at the profile;
#     `message_agent` is injected by Bot Mode at turn time (not a toolset) and survives
#
# Refresh semantics (v2): re-running on an existing profile refreshes config-side
# settings from bot.yaml and the campaign files that exist. If the campaign
# soul.md (or dossier.md) is absent but the profile already has its copy, the
# existing profile copy is KEPT (with a note) — so a bot can be re-verified and
# re-tuned before its persona's canon write lands behind the approval gate.
#
# Model policy: NPCs run the same stack as the GM — default deepseek-flash on the
# deepseek provider (owner call 2026-10-04; supersedes free-OpenRouter-for-NPCs).
# bot.yaml may set `provider:` and `model:`; those defaults apply otherwise.
# Bind = model.default, set to the RAW model id (no alias): an alias value that
# starts with a provider-style vendor token (e.g. "qwen/") gets re-routed by the
# CLI's provider auto-detection to that vendor's own provider (verified 2026-10-04).
# Swap one line:  hermes -p npc-<slug> config set model.default <model-id>
# After any swap, re-pin the sessions: bash bot/npc-maker/repin-model.sh <npc_slug>
# (sessions remember their model; a stale pin keeps the OLD model on resumed turns).
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
mode=""; soulsrc=""; smoke=0
while [ $# -gt 0 ]; do
  case "$1" in
    --verify-only) mode="--verify-only" ;;
    --soul-source) soulsrc="${2:-}"; shift ;;
    --smoke) smoke=1 ;;
    *) echo "unknown option: $1"; exit 2 ;;
  esac
  shift
done
if [ -z "$campaign" ] || [ -z "$slug" ]; then
  echo "usage: make-npc.sh <campaign_id> <npc_slug> [--verify-only] [--smoke] [--soul-source <path>]"; exit 2
fi

src="$REPO/campaigns/$campaign/npcs/$slug"
profile="npc-$slug"
home="$HOME/.hermes/profiles/$profile"
soulsrc="${soulsrc:-$src/soul.md}"

# --- source validation (v2: refresh tolerates missing persona sources) ---
if [ "$mode" = "--verify-only" ]; then
  [ -f "$src/bot.yaml" ] || { echo "FATAL: missing $src/bot.yaml"; exit 1; }
else
  [ -f "$src/bot.yaml" ] || { echo "FATAL: missing $src/bot.yaml"; exit 1; }
  if [ ! -f "$soulsrc" ]; then
    if [ -f "$home/SOUL.md" ]; then
      echo "-- SOUL source absent ($soulsrc) — refresh keeps the profile's existing SOUL.md"
      soulsrc=""
    else
      echo "FATAL: missing SOUL source $soulsrc (a new bot needs soul.md or --soul-source)"; exit 1
    fi
  fi
  if [ ! -f "$src/dossier.md" ] && [ ! -f "$home/dossier.md" ]; then
    echo "FATAL: missing $src/dossier.md (a new bot needs the answered dossier)"; exit 1
  fi
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
  hermes -p "$profile" config set memory.memory_char_limit 1000 >/dev/null
  hermes -p "$profile" config set memory.user_char_limit 500 >/dev/null

  # --- 2b. context isolation (v2): pin a neutral working directory ---
  # Context files (.hermes.md / AGENTS.md / CLAUDE.md / .cursorrules) are discovered
  # from the working directory; without a pin, a turn launched from the repo would
  # load this repo's AGENTS.md and git snapshot into the character's prompt.
  # terminal.cwd is the canonical, scope-aware cwd every consumer reads.
  mkdir -p "$home/workspace"
  hermes -p "$profile" config set terminal.cwd "$home/workspace" >/dev/null

  # --- 2c. tools policy (v2): memory only; message_agent is platform-injected ---
  # Every other toolset is a capability an NPC must never use (web, terminal, files,
  # delegation, cron, …). Disabling them also strips ~40k chars of tool schemas from
  # every turn. Keep list is overridable for a deliberate exception: NPC_KEEP_TOOLSETS.
  keep_toolsets="${NPC_KEEP_TOOLSETS:-memory}"
  all_toolsets="$(hermes -p "$profile" tools list 2>/dev/null | grep -oE '^ *[^ ]+ +(enabled|disabled) +[a-z0-9_]+' | awk '{print $3}' | sort -u | tr '\n' ' ')"
  disable_list=""
  for t in $all_toolsets; do
    keep=0
    for k in $keep_toolsets; do [ "$t" = "$k" ] && keep=1; done
    [ $keep -eq 0 ] && disable_list="$disable_list $t"
  done
  if [ -n "$disable_list" ]; then
    hermes -p "$profile" tools disable $disable_list --platform cli >/dev/null
    echo "-- tools: disabled $(echo $disable_list | wc -w | tr -d ' ') toolsets (keep: $keep_toolsets)"
  fi
  hermes -p "$profile" tools enable $keep_toolsets --platform cli >/dev/null 2>&1 || true

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

  # --- 4. persona + dossier into the profile (v2: keep-existing on refresh) ---
  if [ -n "$soulsrc" ]; then
    cp "$soulsrc" "$home/SOUL.md"
  else
    echo "-- SOUL: kept existing profile copy"
  fi
  if [ -f "$src/dossier.md" ]; then
    cp "$src/dossier.md" "$home/dossier.md"
  else
    echo "-- dossier: kept existing profile copy"
  fi

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
  # guard the spawn against this shell's ambient memory env so no other store is touched;
  # create from the neutral workspace so the chat itself never seeds from operator context
  ( unset TDAI_DATA_DIR TDAI_LLM_API_KEY TDAI_GATEWAY_API_KEY TDAI_GATEWAY_CONFIG \
      TDAI_LLM_MODEL TDAI_LLM_BASE_URL MEMORY_TENCENTDB_LLM_BASE_URL MEMORY_TENCENTDB_LLM_MODEL 2>/dev/null || true
    cd "$home/workspace"
    hermes -p "$profile" chat -c "Bot Chat" --create-if-missing </dev/null >/dev/null 2>&1 || true )
fi

# --- 7. verify ---
echo "== verify =="
echo -n "model.default      : "; hermes -p "$profile" config get model.default 2>/dev/null
echo -n "model.provider     : "; hermes -p "$profile" config get model.provider 2>/dev/null
echo "env                : $(grep -o '^[A-Z_][A-Z0-9_]*' "$home/.env" | sort -u | tr '\n' ' ')"
grep -q 'hermes-bots:' "$home/profile.yaml" && echo "profile.yaml       : Bot Mode marker present" || echo "profile.yaml       : WARN — Bot Mode marker MISSING"
cwdcfg="$(hermes -p "$profile" config get terminal.cwd 2>/dev/null || true)"
if [ -n "$cwdcfg" ] && [ -d "$cwdcfg" ]; then
  echo "terminal.cwd       : $cwdcfg (exists)"
else
  echo "terminal.cwd       : WARN — unset or missing ($cwdcfg) — operator context may leak into prompts"
fi
echo "tools (cli)        : $(hermes -p "$profile" tools list 2>/dev/null | grep -E '^ *✓ enabled' | awk '{print $3}' | sort | tr '\n' ' ')"
echo "memory limits      : memory=$(hermes -p "$profile" config get memory.memory_char_limit 2>/dev/null) user=$(hermes -p "$profile" config get memory.user_char_limit 2>/dev/null)"
[ -f "$home/SOUL.md" ] && echo "SOUL.md            : present ($(wc -c < "$home/SOUL.md" | tr -d ' ') bytes)" || echo "SOUL.md            : WARN — missing"
[ -f "$home/dossier.md" ] && echo "dossier.md         : present ($(wc -c < "$home/dossier.md" | tr -d ' ') bytes)" || echo "dossier.md         : WARN — missing"
sqlite3 "$home/state.db" "SELECT 'bot chat           : '||id||' ('||message_count||' msgs, pin: '||COALESCE(model,'?')||')' FROM sessions WHERE title='Bot Chat' LIMIT 1;" 2>/dev/null || echo "bot chat           : WARN — not created yet"

# --- 8. live smoke (opt-in): one delivery-style turn into the Bot Chat ---
if [ "$smoke" = "1" ]; then
  echo "== smoke (live turn into the Bot Chat; adds one line + reply) =="
  qfile="$(mktemp -t npc-smoke.XXXXXX)"
  printf 'Voice check — one short line in character, no plot, nothing else.' > "$qfile"
  ( unset TDAI_DATA_DIR TDAI_LLM_API_KEY TDAI_GATEWAY_API_KEY TDAI_GATEWAY_CONFIG \
      TDAI_LLM_MODEL TDAI_LLM_BASE_URL MEMORY_TENCENTDB_LLM_BASE_URL MEMORY_TENCENTDB_LLM_MODEL 2>/dev/null || true
    cd "$home/workspace"
    hermes -p "$profile" chat -c "Bot Chat" -Q --query-file "$qfile" 2>&1 ) | sed '/^session_id:/d' | tail -n 12
  rm -f "$qfile"
  logline="$(grep 'conversation turn' "$home/logs/agent.log" 2>/dev/null | tail -1 || true)"
  if [ -n "$logline" ]; then
    echo "smoke evidence     : $logline"
  else
    echo "smoke evidence     : WARN — no conversation-turn line in agent.log"
  fi
fi

echo "== done: $profile =="
