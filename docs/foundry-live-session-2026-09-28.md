# Foundry Live-Session Handoff — 2026-09-28 (updated 2026-09-29 ~01:05 PT)

**Read this first. Everything lives on disk; nothing critical lives in the old conversation.**

**Role setup:** I am the AI Gamemaster for Delta Green. Chris = the player. Hard rule: all live play happens where Chris can see it.

---

## End-of-night update — 2026-09-29 ~01:05 PT

- **Game left UNPAUSED.** Cleared 00:06:50 (`Toggling game pause status to false`); nothing re-paused since — verified via log (only 1 pause line all night) + AX scans + screenshots. Chris closed the night playing.
- **Pause mechanics (source-verified v14.365):** GM-seat-only on both ends — client `keyboard-manager.mjs` (`restricted && !isGM` skip) + server `Activity.pause()` (`isGM` gate; logs every GM toggle, silently drops non-GM). Players can NEVER pause; a pause banner with no `to true` log line = state carried from earlier, not a new toggle. Clear = single **background** `press_key` Space to the GM window (6555 / Firefox pid 78342); verify log line + no `PAUS` element. No clickable pause control exists.
- **iPad "Undo Typing" popup = iPadOS shake-to-undo** (motion/gestures), not the game — cannot pause anything. Fix: Settings → Accessibility → Touch → Shake to Undo → OFF. The "MISSION PAUSED on the iPad only" scare = **stale frozen tab**; a full page reload cleared it (confirmed working).
- **Zero actors in the world** (store empty; Chris's user `character` = null). Chris hit the User Config "Player Character" picker being empty — explained: it only lists actors he can see, and creates nothing; first Create Actor (Actors tab → Create Actor → type *Agent*), then reopen the picker. Player role CAN create actors (`core.permissions` `ACTOR_CREATE:[1,3,4]`).
- **Next session:** cue from Chris → walk him through building the Agent. Stats = **4D6 drop lowest, six times, assign as desired** (official quick-start method; corrected 09-29 — the earlier "×5 / 80-70-60-60-50-50 array" line in this doc was wrong/unverified, ignore it). Full chargen quick-reference at the bottom of this doc.

---

## Current state (ALL SYSTEMS WORKING)

- Foundry VTT: launchd `com.hermes.foundryvtt`, port 30000, **bound `*:30000`** (LAN + Tailscale OK). World `deltagreen` **RUNNING**.
- **Chris's seat = passwordless** (pbkdf2 of empty string — verified). Joins with: pick Chris → empty password → JOIN.
- **Gamemaster seat = passwordless AND LOGGED IN** (auth success 22:57:11, "users":1) — logged in from Firefox window 6555 on the Mac. The AI GM is physically in the world.
- **Player role NOW CAN create actors + items** — patched `core.permissions` in the world settings db (`ACTOR_CREATE:[1,3,4]`, `ITEM_CREATE:[1,3,4]`; was `[3,4]`).
- World URL for iPad/other devices: **http://100.116.128.73:30000** (Mac's Tailscale IP; sent to Chris for his iPad).
- Firefox's stale saved login for localhost:30000 = **DELETED** (about:logins → Remove). This was the root cause of ~an hour of failed joins. The field on the join page now comes up empty.
- Red "window dimensions" warning = resolved via ⌘⇧B (bookmarks bar folded).
- Users-db backup: `~/.hermes/cache/scratch/foundry-users-backup-<ts>-users`.

## The auth mechanism (cracked from source: `dist/core/auth.mjs`, `dist/sessions.mjs`)

- Stored password = **pbkdf2Sync(password, passwordSalt, 1000, 64, 'sha512').hex** (128 hex chars); passwordSalt = 64 hex chars.
- **Passwordless = pbkdf2 of the EMPTY STRING**; the join page submits exactly what's in the password field.
- **ALWAYS verify the field's AX value reads empty before clicking JOIN** — any stray char (or Firefox autofill) fails with "invalid password".
- Users db at `.../data/worlds/deltagreen/data/users` — **LevelDB, LOCKED while the world runs**. Writes happen with the world stopped, using the **two-phase pattern** (drain iterator → then puts). Scripts: `fix2.js` (users), `perms-fix.js` (settings), `verify3.js` / `perm.js` (verify by copy).
- World settings db at `.../data/worlds/deltagreen/data/settings` (same rules). `core.permissions` holds the role→action map.

## Headless world stop/launch (no UI, no launchctl — it's gateway-blocked!)

Admin password lives in `~/.hermes/profiles/ttrpg/.env` (key `FOUNDRY_ADMIN_PASSWORD`). **Never echo it.** Procedure:

```bash
PW=$(grep '^FOUNDRY_ADMIN_PASSWORD=' ~/.hermes/profiles/ttrpg/.env | cut -d= -f2-)
JAR=~/.hermes/cache/scratch/fj.txt
# STOP (admin pw in body → session marked admin; expect {"status":"success","message":"The game world has been successfully deactivated"})
curl -s -c $JAR -X POST http://127.0.0.1:30000/join -H 'Content-Type: application/json' \
  -d "{\"action\":\"shutdown\",\"adminPassword\":\"$PW\"}"
# (world stopped → DBs unlocked → run fix2.js / perms-fix.js → verify on fresh copies)
# LAUNCH (same admin-marked jar)
curl -s -b $JAR -c $JAR -X POST http://127.0.0.1:30000/setup -H 'Content-Type: application/json' \
  -d "{\"action\":\"launchWorld\",\"world\":\"deltagreen\",\"adminPassword\":\"$PW\"}"
```

Note: a world stop+launch drops all live sessions (everyone re-joins; passwordless seats = two clicks).

## Character creation (Chris's ask — NOW UNBLOCKED)

- Chris (player) can now: Actors sidebar → Create Actor → name + type **Agent** → sheet opens (tabs: stats/skills/gear/bonds...).
- Two stat methods (system-supported): roll **4d6-drop-lowest ×5**, or the array **80/70/60/60/50/50**.
- Alternative: pull from the deltagreen system's pregens compendium (~26 agents: NORD, CARSON, RAASCH, SNIPES…), or the Convergence module compendium for adventure content.
- Standing campaign rules: never invent sample adventures/content; no unrequested scaffolding; verify against the real runtime.

## cua-driver receipts (macOS screen driving)

- Binary: `/Applications/CuaDriver.app/Contents/MacOS/cua-driver`. Key calls: `get_window_state`, `click`, `press_key` (delivery_mode foreground), `type_text`, `bring_to_front`, `list_windows`, `get_desktop_state`, `invoke_menu`.
- `bring_to_front` before foreground key batches (want `_verified`); `_unverified` = keys may land elsewhere.
- Join flow that works: fresh **private** window → `cmd+L` + URL → read dropdown/field AX values → type-ahead single letter on the dropdown (`c`/`g`, foreground) → VERIFY field empty → click JOIN → check log "User authentication successful" + `/api/status` users count.
- Firefox 156 here can autofill saved logins even in private windows — the saved-login delete is the permanent fix.
- The driver's own overlay window = Cua Driver (pid 19439); ignore it in window lists.

## Loose ends

- `FOUNDRY_GM_PASSWORD` in `profiles/ttrpg/.env` = STALE (never worked; seats are passwordless now) — clean up sometime.
- Desktop tidy request (3 items: `div_divs_daily_driver_quiz.html`, `Hermes Agent Dasboard_files`, `dnd dictator`) — MOVE not copy — still queued.
- ttrpg profile (`~/ttrpg_gm`) = campaign home + bridge (mcp_foundry_* tools); this session = default profile.
- After any FF restart a "Restore Session" page may appear — dismiss casually.
- The world-file lock (launchd server holds it) is why deletes/overwrites bounce — stop the service before any destructive world operation (see headless stop/launch above).

---

## Chargen quick-reference — added 09-29 (verified against system source v1.7.0 + live world DB)

- **New Agent actors** are created with every stat = 10 ("average adult") and DG's standard **base skills** pre-loaded (Accounting 10, Alertness 20, Athletics 30, … Unarmed Combat 40). That is the legal starting state, not filler — profession points layer on top later.
- **Generation (official):** roll **4D6 drop lowest, six times**, assign the six results among STR/CON/DEX/INT/POW/CHA (stats run 3–18). The base system has **no stat-generation roller** — the only rolling it does is *tests* (tap a stat's name label on the sheet → test vs stat ×5). Chris rolls his own dice.
- **Entry UI:** left bar of the sheet → tiny **✎ pen button ("Edit Stats")** → opens the "Edit statistics form" (six fields + distinguishing features; live-submits as typed; action `openStatsEdit`).
- **Derived values:** HP max = ⌈(STR+CON)/2⌉ and WP max = POW recompute **automatically** on update. **SAN does NOT auto-follow** (manual by design — value ≥100 is the init sentinel only): after entering stats, set SAN = POW×5, reset Breaking Point via the ♻ icon (SAN − POW), and bump current HP/WP values up to the new maxes. SAN max = 99 − Unnatural.
- **Musky Jouse** = Chris's Agent actor (key `!actors!ap0mI1aC5BFJDL7O`), created 09-29 ~05:45 PT; stats still 10s pending his rolls. A stray second "Create Actor" dialog was open on his iPad — watch for a duplicate "Agent" actor.
- **Not installed:** community module `delta-green-agent-wizard` (full chargen wizard: stats incl. 4d6-drop-lowest roll, all official professions, skills, bonus picks, bonds, gear, DD-315 PDF export; declares Foundry v13+). Offered to Chris 09-29 — if he accepts: install + verify on Foundry 14.365 first.
- **Verify after edits:** read the actor from a copy of `data/actors` (LevelDB; copy-then-read pattern) with scratch script `foundry-db/dump-actor.js` (mirror of the users-db tooling; scratch may be pruned — recreate per pattern).
- **Update 09-29 ~06:20 — Musky Jouse finished:** stats 14 / 14 / 14 / 16 / 15 / 16; HP 14/14, WP 15/15, SAN 75, BP 60. (Chris set SAN + BP himself; HP/WP current+max were still 10 → written directly to the actors db during a world stop with `wiz-op` pattern / `fix-actor.js`.) Backups: `~/.hermes/cache/scratch/wiz-op/`.
- **Sheet version:** default = **v1 agent sheet** (`DGAgentSheet`; V2 exists in system 1.7.0 but its registration is commented out). Tabs: Skills / Statistics / Psychological / Equipment / Bio / Bonds. Breaking Point field + "Reset" button live on the **Psychological** tab; the `♻` icon and left-bar layout are V2-only — don't reference them.
- **Module `delta-green-agent-wizard` v0.1.1 installed + activated** (community chargen wizard: stats / professions / skills / bonus picks / bonds / bio / equipment, DD-315 PDF export). **CORRECTION 09-29: v14 module activation = the `core.moduleConfiguration` world setting, NOT world.json's `modules` array (details in the update below).** Needs world stop→launch (bounce recipe below). Gotcha: `installPackage`'s HTTP call resolves `{}` when the *download* finishes while extraction continues async — check for the extracted module dir before declaring failure.
- **World bounce recipe re-verified 09-29:** `POST /join {action:"shutdown", adminPassword}` (marks session admin) → edit/verify world.json → `POST /setup {action:"launchWorld", world:"deltagreen", adminPassword}` same cookie jar. Foundry app log: `/Users/chriscoon/.hermes/logs/foundry.log`. Next op on the docket: Chris runs the wizard — recommend **Federal Agent**; do the Skills/Bonus step together (solo-proofing).
- **Update 09-29 ~06:45 — Wizard live; root causes; state preloaded:**
  - **v14 module activation lives in the `core.moduleConfiguration` world setting — NOT world.json's `modules` array.** Client script tags + per-module `active` flags both derive from that setting (`m[e.id] ?? false` in world.mjs; `_getStaticContent({moduleConfig})` in the game view). Editing world.json "modules" alone does nothing — the fix that worked: set `{"delta-green-agent-wizard": true}` in the settings LevelDB while the world is stopped (`wiz-op` backup: `settings-backup-20260929-063046`). Verified end-to-end by logging in as user `mcp-api` (password = `MCP_FOUNDRY_PASSWORD` in the ttrpg `.env`; `POST /join {action:"join",userid,password}`) and confirming `/game` HTML serves `modules/delta-green-agent-wizard/scripts/main.js`.
  - **Wizard state preload mechanics:** `wizard.js` persists to actor flags `delta-green-agent-wizard.wizardState = {step, data}` and merges saved state over its defaults on open. Preloaded Musky directly (flags write while world stopped; backup `actors-backup2-20260929-064807`): stats 14/14/14/16/15/16, bio name "Musky Jouse", step 1 (Statistics).
  - **Wizard gotchas:** profession must be picked in the UI — pre-filling `professionKey` skips the required-skills build (`profChanged` guard in collect). Stats step: no sum validation (72 = guidance only; direct number entry, 3–18 per stat). Bonus skills = 8 slots × +20%, cap 80. Apply recomputes HP/WP/SAN/BP from stats (lands on current 14/15/75/60) and unsets the flag on Finish.


## Update 2026-09-29 ~08:15 — Hermex incident & repair (ops)

Chris launched the game via Hermex (ttrpg profile) ~07:21. The session started, but the
WebUI-hosted bot had **no mcp_foundry_* tools and no memory gateway** (both are wired through
env the webui process didn't have). The bot self-diagnosed, armed a Hermex restart; that
restart hit a bootstrap crash loop and Hermex went down ~07:52.

Root causes (all fixed, verified):
1. **Memory gateway dead** — `MEMORY_TENCENTDB_GATEWAY_CMD`'s nested `sh -c '…'` quoting broke
   (`No closing quotation`); the supervisor spawns via `shlex.split()`. Replaced with a quote-free
   launcher: `~/.hermes/scripts/memory-gateway-launch.sh <profile>` (ttrpg + ssdi `.env` updated).
2. **WebUI cannot restart under launchd** — bootstrap "cannot import both WebUI dependencies and
   Hermes Agent" (repo `.venv` shim can't import `yaml` in a minimal env). Fixed: installed
   `~/hermes-webui/requirements.txt` into the agent tools python + pinned `HERMES_WEBUI_PYTHON`
   in `~/hermes-webui/.env` (mode 600).
3. **WebUI-hosted sessions lacked MCP creds** — `${env:MCP_FOUNDRY_PASSWORD}` resolves from the
   webui process env, not the profile `.env`. Added the var to `~/hermes-webui/.env`
   (start.sh sources it with `set -a`). Verified in-process (`ps eww` count).
4. Batch of deleted files restored from git: `~/hermes-webui` (4, incl. `api/config.py` — imported
   at server start) and `~/ttrpg_gm` (21, incl. AGENTS.md + 2 bot skills). STATUS.md refreshed.

Verified after repair: smoke → `35 mcp_foundry tools`, memory search returns matches, gateway
spawns via launcher in ~15–25s. Hermex serving on local + Tailnet. **Play resumes in a NEW chat**
(the old "Musky Jouse Convergence Session" context is all debugging).

## Update 2026-09-29 ~08:25 — play begins (session 5a0668bb1923)

- The fresh chat seated **without** `mcp_foundry_*` tools again — session-level seat still unresolved (webui proc env carries `MCP_FOUNDRY_PASSWORD` [checked]; bridge itself green: CLI re-test 08:20:54 → connected, world vended 839ms, full tool set). No spawn for this session in `mcp-stderr.log`.
- Player elected to start anyway: play runs **narrative-first** from session `5a0668bb1923`; sheet changes coached by hand; Foundry writes reconciled when the seat heals. World up (14.365, 0 users online @ 08:25).
- Watcher still armed: `~/.hermes/profiles/ttrpg/cache/scratch/mcp_watcher.sh` → `mcp-watch.log` (captures next webui→foundry seating attempt).
- Stale npx procs from 09-28 21:05 (`42179`/`42212`) still resident; inert.
- Musky Jouse intact: Federal Agent · HP 14/14 · WP 15/15 · SAN 75 · BP 60. *Convergence* opened at the Knoxville briefing.
- Player canon (09-29): Musky spent six months undercover inside the Mongols MC (eastern TN); girlfriend **Anu** (autumn leaves). Style doctrine set by owner: novel-like interiority, character development first, relationships paramount, nuanced non-cliché NPCs — written into `bot/skills/ttrpg-narrator.md` ("Character & Relationship Doctrine").
- New directives (owner, 09-29): **"Prohibited Clichés" registry** created in `bot/skills/ttrpg-prohibitions.md` (standing set + owner-verbatim additions; item 1 = vibration/thrumming/humming/oscillating/pulsing descriptions, unless literal in the adventure). Crunchy mechanics + active coaching + stop-at-every-roll filed in `ttrpg-campaign-tools.md` ("Table & Mechanics Doctrine"); dialogue-first fill-in doctrine added to `ttrpg-narrator.md`.
- **NPC bot loaded (2026-10-04 ~22:10):** Billy Ray Spivey bot activated for play — GM-side `Bot Chat` created (`20261004_221017_a2c202`); live round-trip proven (GM → `message_agent` → Billy's Bot Chat → in-voice reply, ~seconds). Also re-pinned his Bot Chat's stale qwen-era session model (row + billing → deepseek-flash; backup in his `backups/`), verified via live turns — `model=deepseek-flash`, `provider=deepseek`, ~2s. Deep Billy beats route through his bot; flavor stays inline. Mechanism: `ttrpg-npc-bots` skill + `bot/npc-maker/README.md`.

## Update 2026-10-08 — NPC bot roster expanded (pre-Groversville)

Five more Convergence NPC bots built end-to-end and voice-checked — plus Billy,
the roster is six: **Sheriff Dan Oakley** (`npc-dan-oakley`), **Frank Carincola**
(`npc-frank-carincola`), **Jane Allen** (`npc-jane-allen`), **Angel Spivey**
(`npc-angel-spivey`), **James Derringer** (`npc-james-derringer`). Dossiers in
`campaigns/delta-green-convergence/npcs/<slug>/dossier.md` (first drafts pending
the owner's pass). Deep beats route through the NPC bots via the GM Bot Chat;
flavor stays inline. **Bot-voice marker in force:** bot-spoken lines carry a
caret before the opening quote in the relayed fiction (`^"…"`) — the owner's
standing signal; doctrine in `bot/skills/ttrpg-campaign-tools.md` +
`bot/npc-maker/README.md`.
