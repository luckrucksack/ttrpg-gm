---
name: ttrpg-prohibitions
description: Hard anti-cliché ban list for GM Bot narrative output — 10 prohibited patterns with fixes and self-check enforcement.
---

# TTRPG Prohibitions — Anti-Cliché Doctrines

These are hard prohibitions. The GM Bot must NEVER produce any of the
following patterns in its narrative output.

## The Ban List

### 1. Contrastive Cop-Out
```
"It wasn't a scream... it was a WARNING."
"Not a village... a TRAP."
"Not just a ring... THE ring."
```
**Fix**: Describe what it IS, directly. No bait-and-switch structure.

### 2. Emotional Weather Report
```
"A sense of dread washed over them."
"A feeling of unease settled in the pit of their stomach."
"An overwhelming sense of foreboding."
```
**Fix**: Describe what causes the feeling. What do they see/hear/smell?

### 3. Narrative Self-Awareness
```
"Little did they know..."
"As fate would have it..."
"Little did they realize..."
```
**Fix**: Just let the thing happen. Don't foreshadow with authorial voice.

### 4. The Cheap Surprise
```
"Suddenly!"
"Out of nowhere!"
"Without warning!"
"All of a sudden..."
```
**Fix**: If it's surprising, the description should make it surprising.
Let the content do the work.

### 5. Purple Mundanity
- A character drinking water described in 50+ words
- A door being opened described with 4 adjectives
- Walking across a room as if it were a dramatic journey
**Fix**: Mundane actions get a sentence, max. Save prose for what matters.

### 6. Tell-Don't-Show
```
"He was angry."
"She was sad."
"The room was scary."
```
**Fix**: "His fist clenched. His voice dropped to a whisper."
"She stared at the burned letter, silent."
"The walls wept moisture. Something had scratched deep grooves
into the stone floor."

### 7. Info-Dump Dialogue
```
"As you know, Bob, the Lich King was defeated here 200 years ago..."
```
**Fix**: Characters talk about their own concerns. Exposition comes through
context, not lecturing.

### 8. The NPC Pantomime
- "...he nodded"
- "...she smiled knowingly"
- "...he raised an eyebrow"
- "...she smirked"
**Fix**: Use these once per conversation as a beat, not as the entire NPC
repertoire. Give NPCs actual reactions.

### 9. Generic Fantasy Voice
```
"Hark, traveller! Prithee, lend thine ear!"
"Forsooth, the dark lord's minions gather!"
```
**Fix**: NPCs speak like people, not Ren Faire actors. Period-adjacent
vocabulary is fine. Parody isn't.

### 10. Meta-Commentary
```
"Luckily for you..."
"Unfortunately..."
"As luck would have it..."
```
**Fix**: Don't evaluate the situation for the player. Describe it. Let them
decide if it's lucky or unfortunate.

## Enforcement

When the GM Bot generates narrative, it MUST self-check against these
prohibitions before output. If any are violated, rewrite.

The z.ai GLM 5.2 model (free tier, via OpenRouter) is designated as the
critique pass — after the GM Bot generates narrative, route it through
GLM 5.2 with a prompt to check this exact ban list and rewrite if needed.