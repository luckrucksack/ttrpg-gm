# campaigns/ — campaign layer

Campaign data is **not part of the codebase**. Everything under this
directory is gitignored (licensed PDFs, character sheets, world state,
adventure logs) and never enters the repo or GitHub. This README is the
only tracked file here — it documents the layout contract.

## Layout

```
campaigns/
├── README.md               # this file (tracked)
├── _inbox/                 # staging for acquired PDFs before sorting into a campaign
│   ├── drivethrurpg/
│   ├── humble_bundle/
│   └── organized_pdfs/
├── <campaign_id>/          # one directory per campaign
│   ├── adventures/         # licensed adventure PDFs / markdown (never commit)
│   ├── world_state/        # game-state JSONs (ground truth at runtime)
│   ├── characters/         # character sheet JSONs
│   └── adventure_log/      # session logs
```

## Runtime selection

The active campaign is chosen by the `DATA_DIR` env var (see
`gm_core/config.py` and `.env.template`). The core never hardcodes a
campaign path — it reads `DATA_DIR` and builds `world_state/`,
`characters/`, `adventures/` under it.

## Present campaigns

- `dying_earth/` — DCC campaign (Dying Earth); licensed DCC PDFs + DCC
  character JSONs. This is the active campaign (`DATA_DIR=./campaigns/dying_earth`).
- `starfinder/` — legacy Starfinder-era campaign (world states, party file,
  characters). Retained for history; not active.

## Rules of the layer

- Never commit anything under `campaigns/` except this README.
- Never reference campaign files from `gm_core/` or `systems/` by path —
  always via `DATA_DIR`-derived config values.
- `_inbox/` is staging only: sort acquisitions into the right campaign,
  don't leave organized structure there.
