# campaigns/ — campaign data layer

Campaign data is **not part of the codebase**. Everything under this directory is
gitignored (licensed PDFs, character sheets, world state, session logs) and never
enters the repo or GitHub. This README is the only tracked file here — it
documents the layout contract.

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
│   └── source/             # any local module/JSON source material (never commit)
```

## How campaign data flows in this architecture

- **Foundry VTT** is the source of truth for world state at the table: actors,
  scenes, combat, journals imported from adventures.
- **TencentDB Agent Memory (:8421)** holds campaign narrative state: session
  logs, NPC relationship state, plot threads.
- This directory holds only the **source material** (licensed PDFs, purchased
  modules, local notes) that feeds the ingestion pipeline:

```
campaigns/<id>/adventures/foo.pdf  →  pipeline/ingest.py  →  pipeline/output/foo/
                                                              → GM Bot imports via Foundry MCP
```

Nothing under `campaigns/` is read at runtime by the bot or the pipeline except
the file you point `ingest.py` at.

## Rules of the layer

- Never commit anything under `campaigns/` except this README.
- `_inbox/` is staging only: sort acquisitions into the right campaign,
  don't leave organized structure there.