# AI TTRPG Game Master System

An autonomous AI Game Master that bridges adventure PDFs, DeepSeek API, and Discord. Nothing reaches players without passing through the automation engine first.

## 🎯 Core Philosophy

**You are the local automation engine for an AI Game Master.** You bridge adventure PDFs, the DeepSeek API, and Discord. Nothing reaches players without passing through you first.

## ✨ Features

### ✅ **Complete System**
- **Adventure Processing**: Extract text from PDFs, build world state, prime AI context
- **Character Management**: Real-time JSON tracking of HP, conditions, inventory, abilities
- **Runtime Loop**: Listen → Assemble → Call → Arbitrate → Refine → Deliver
- **Directive System**: `[REQUEST_ROLL]`, `[UPDATE_STATE]`, `[UPDATE_CHARACTER]`, `[MOVE_SCENE]`
- **Two-Stage Refinement**: Raw AI output never reaches players
- **Local Dice Rolling**: No external RNG, full audit trail in Discord
- **Override/Resync**: `!override` to halt, `!resume` to reconcile

### 🏗️ **Architecture**
```
ttrpg_gm/
├── data/
│   ├── adventures/          # Source PDFs
│   ├── world_state/         # Game state JSONs
│   └── characters/          # Character sheet JSONs
├── agents/
│   ├── discord_bridge.py    # Discord listener and poster
│   ├── dice_roller.py       # Local dice rolling engine
│   ├── prose_refiner.py     # Two-stage refinement
│   └── pdf_ingestor.py      # PDF parsing
└── main.py                  # Central automation loop
```

## 🚀 Quick Start

### 1. Installation
```bash
# Clone or extract to your machine
cd ttrpg_gm

# Run setup script
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

### 2. Configuration
```bash
# Edit .env with your credentials
nano .env
```

Required environment variables:
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_GAME_CHANNEL_ID=your_discord_channel_id_here
```

### 3. Import Adventures
```bash
# Place PDFs in data/adventures/
# Then import them
python main.py --import data/adventures/lost_mine.pdf lost_mine
```

### 4. Run the System
```bash
# Start the AI GM
python main.py lost_mine
```

## 📋 Operational Specification

### On Startup
1. Verify Discord bot token
2. Verify DeepSeek API access  
3. Verify local data directories
4. **Halt and report any failure**

### Character Sheets
- Ingest player character PDFs → `data/characters/[name].json`
- Track: HP, spell slots, conditions, inventory, abilities, class resources, passive scores
- **Update JSON immediately when any value changes**

### Adventure Ingestion
When given an adventure PDF:
1. **Extract all text** — room descriptions, read-aloud text, monster stats, traps, treasure, encounter tables, NPC data, special rules
2. **Build world state** — `data/world_state/[adventure].json` with rooms keyed by location ID, monster HP, trap triggers, encounter flags, stateful variables
3. **Prime DeepSeek** — send full extracted adventure text plus system rules as system context

### Runtime Loop (Execute every turn)
1. **Listen** — monitor Discord game channel for player messages
2. **Assemble context** — bundle player message, current scene, character stats, monster stats, recent history
3. **Call DeepSeek** — instruct to respond with narrative + directives (`[DIRECTIVE: parameters]`)
4. **Arbitrate directives** before any refinement:
   - `[REQUEST_ROLL: NdX+modifier]` → execute local roll → post to Discord → feed back to DeepSeek
   - `[UPDATE_STATE: field, value]` → update world_state.json immediately
   - `[UPDATE_CHARACTER: character, field, value]` → update character JSON immediately
   - `[MOVE_SCENE: location_id]` → load new room data
5. **Refine** — run both prose refinement stages
6. **Deliver** — post final text to Discord. Wait. Do not post again until player responds.

### Two-Stage Prose Refinement
**Raw DeepSeek output never reaches players.**

**Stage 1 — Dialectic Removal:**
```
Identify every contrastive or antithesis structure in this text — 
constructions such as "It's not A, it's B," "Not just X, but Y," 
or any pattern that negates or diminishes something in order to 
elevate something else. Rewrite each instance as a direct affirmative 
statement. Change nothing else. Return only the rewritten text.
```

**Stage 2 — Literary Rewrite:**
```
You are a literary editor working on atmospheric fiction. 
Rewrite this passage for pacing, sensory specificity, tonal consistency, 
and immersive detail. It should read like skilled prose, not chatbot output. 
Preserve all game-mechanical facts exactly. Return only the rewritten passage.
```

### Dice Rolling
- **Local dice roller only** — never calls external bots for randomness
- After every GM-side roll, **post result visibly to Discord** so full roll history remains auditable
- Player rolls are made directly by players in channel; system captures result for next context bundle

### Override and Resync
- `!override` — immediately halt all API calls, dice rolls, state updates, and posting
- `!resume` — re-read all JSONs from disk, review Discord history for anything during pause, reconcile into coherent context, then re-enter runtime loop

## 🎮 Directives Reference

### `[REQUEST_ROLL: NdX+modifier]`
- Executes local dice roll
- Posts result to Discord with full details
- Feeds result back to DeepSeek
- Awaits narrative continuation

**Examples:**
- `[REQUEST_ROLL: 1d20+5]` — Standard ability check
- `[REQUEST_ROLL: 2d6+3]` — Weapon damage
- `[REQUEST_ROLL: 8d6]` — Fireball damage

### `[UPDATE_STATE: field, value]`
- Updates `world_state.json` immediately
- Field can use dot notation: `rooms.dungeon.door.locked`
- Value can be string, number, or boolean

**Examples:**
- `[UPDATE_STATE: rooms.cave.chest.opened, true]`
- `[UPDATE_STATE: npcs.merchant.attitude, friendly]`
- `[UPDATE_STATE: monsters.goblin.chief.hp, 12]`

### `[UPDATE_CHARACTER: character, field, value]`
- Updates character JSON immediately
- Field can use dot notation: `hp.current` or `inventory.0.quantity`

**Examples:**
- `[UPDATE_CHARACTER: thoradin, hp.current, 24]`
- `[UPDATE_CHARACTER: elara, conditions, ["poisoned"]]`
- `[UPDATE_CHARACTER: gimli, inventory.2.quantity, 3]`

### `[MOVE_SCENE: location_id]`
- Loads new room data into next context bundle
- Updates current location in world state

**Examples:**
- `[MOVE_SCENE: room_7]`
- `[MOVE_SCENE: throne_room]`
- `[MOVE_SCENE: forest_clearing]`

## 🔧 Technical Details

### State Management
- **JSONs are ground truth** — if DeepSeek's assumptions conflict with a JSON, the JSON wins
- **State updates happen immediately** when triggered, never deferred
- **Thread-safe operations** with proper locking
- **Automatic backups** before overwrites

### Error Handling
- **Startup validation** — halts on any configuration failure
- **API failure fallbacks** — continues with degraded functionality
- **Discord reconnection** — automatic reconnection attempts
- **State corruption protection** — backups and validation

### Performance
- **In-memory caching** of frequently accessed data
- **Async/await architecture** for non-blocking operations
- **Efficient context assembly** — only relevant data included
- **Token usage tracking** — monitor API costs

## 🛠️ Development

### Adding New Directives
1. Add directive type to `DeepSeekClient.extract_directives()` pattern
2. Implement handler in `AIGameMaster.process_directive()`
3. Add to system prompt in `DeepSeekClient.prime_with_adventure()`

### Extending PDF Parsing
The `PDFIngestor` class uses multiple extraction methods:
1. `pdfplumber` for formatted text
2. `PyPDF2` as fallback
3. Custom regex patterns for structure

Add new patterns to the `_extract_*` methods.

### Customizing Refinement
Override `ProseRefiner` methods:
- `_stage1_dialectic_removal()` — custom dialectic patterns
- `_stage2_literary_rewrite()` — different literary styles
- `_build_context_description()` — context formatting

## 📊 Monitoring

### System Statistics
```bash
# Printed on shutdown
Runtime: 2024-01-01T12:00:00 to 2024-01-01T14:30:00
Turns processed: 42
Dice rolled: 18
Messages sent: 42
DeepSeek tokens used: 15,234
Conversations: 42
World states: 3
Characters: 5
```

### Log Files
- `logs/system.log` — General system events
- `logs/discord.log` — Discord interactions
- `logs/api.log` — DeepSeek API calls
- `logs/state.log` — State changes

## 🚨 Non-Negotiable Rules

1. **Raw DeepSeek output never reaches players.** Both refinement stages always run.
2. **All randomness comes from your local dice roller.** Results are always posted to Discord.
3. **JSONs are ground truth.** If DeepSeek's assumptions conflict with a JSON, the JSON wins.
4. **State updates happen immediately when triggered, never deferred.**

## 🤝 Contributing

### Code Style
- **Black** formatting
- **Type hints** for all function signatures
- **Docstrings** for all public methods
- **Async/await** for I/O operations

### Testing
```bash
# Run tests
pytest tests/

# Test specific component
python -m agents.dice_roller
python -m agents.pdf_ingestor
```

### Pull Requests
1. Update documentation
2. Add tests for new features
3. Update `.env.template` if adding new environment variables
4. Update `requirements.txt` if adding dependencies

## 📄 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- **DeepSeek** for the AI API
- **Discord** for the communication platform
- **Open source PDF libraries** for text extraction
- **The TTRPG community** for inspiration

## 🆘 Support

### Common Issues

**Discord bot not connecting:**
- Verify bot token
- Check channel ID (enable Developer Mode)
- Ensure bot has proper permissions

**DeepSeek API errors:**
- Verify API key
- Check rate limits
- Ensure proper billing setup

**PDF parsing issues:**
- Try different PDF library: `pip install pymupdf`
- Convert PDF to text first
- Use OCR for scanned PDFs

**State corruption:**
- Check `.bak` backup files
- Manual edit of JSON files
- Restore from backup

### Getting Help
1. Check `logs/` directory for error details
2. Run `python test_system.py` to verify components
3. Enable debug logging: `LOG_LEVEL=DEBUG`
4. File GitHub issue with logs and reproduction steps

---

**Remember:** You are the automation engine. The AI proposes, you execute, players experience. Nothing reaches players without passing through you first.