# DCC Judge Quick-Start Guide

**Created:** March 22, 2026, 4:35 AM  
**System:** Dungeon Crawl Classics Judge  
**Campaign:** Dying Earth  
**Status:** Ready for immediate testing

## 🚀 Immediate Testing Setup

### **1. System Status Check**
```bash
# Check DCC Judge is ready
cd /Users/chriscoon/ttrpg_gm
python3 dcc_judge.py --status
```

### **2. Load Pre-Generated Characters**
Characters are ready at: `/Users/chriscoon/ttrpg_gm/data/characters/`
- `dying_earth_noble.json` - Lord Valerius (Warrior)
- `dying_earth_thief.json` - Silk the Shadow-Dancer (Thief)
- `dying_earth_wizard.json` - Zephyrim the Last Geomancer (Wizard)
- `dying_earth_cleric.json` - Sister Solara (Cleric)

### **3. Test DCC Mechanics**

#### **Spellburn Test (Wizard)**
```python
# Test spellburn mechanics
python3 dcc_judge.py --character dying_earth_wizard.json --action spellburn --ability strength --amount 2
```

#### **Luck System Test**
```python
# Test luck burning
python3 dcc_judge.py --character dying_earth_noble.json --action burn-luck --amount 3
```

#### **Corruption Check**
```python
# Check corruption tracking
python3 dcc_judge.py --character dying_earth_wizard.json --action check-corruption
```

### **4. Sample Gameplay Scenario**

**Adventure:** "The Dying Sun's Last Whisper" (Dying Earth adventure #1)

**Setup:**
```python
python3 dcc_judge.py \
  --adventure dying_sun_last_whisper \
  --characters dying_earth_noble.json,dying_earth_thief.json,dying_earth_wizard.json,dying_earth_cleric.json \
  --start-scene "The party stands before the Sunken Observatory, where ancient astronomers charted the sun's decay."
```

**Sample Commands:**
```python
# Move to first scene
python3 dcc_judge.py --action move-scene --scene "Observatory Entrance"

# Make perception check
python3 dcc_judge.py --character dying_earth_thief.json --action roll --skill perception

# Cast spell with spellburn
python3 dcc_judge.py --character dying_earth_wizard.json --action cast-spell --spell "Magic Missile" --spellburn agility 1
```

## ⚙️ DCC Mechanics Testing Checklist

### **Core Mechanics to Validate:**
- [ ] **Spellburn:** Wizard can burn STR/AGI/STA for spell power
- [ ] **Corruption:** Failed spells track corruption manifestations
- [ ] **Luck System:** Characters can burn luck points
- [ ] **Mercurial Magic:** Wizard's spell has unique d8 effect
- [ ] **Crit/Fumble Tables:** Class-specific tables work
- [ ] **Thief Skills:** 1-in-6 to 3-in-6 progression functions
- [ ] **Turn Undead:** Cleric can attempt to turn undead
- [ ] **Mighty Deeds:** Warrior can attempt deeds with d3 die

### **Literary Style Testing:**
- [ ] **Dying Earth Prose:** Two-stage refinement applies Jack Vance style
- [ ] **Character Voice:** Each character's thematic elements reflected in prose
- [ ] **Atmospheric Descriptions:** Scene descriptions match Dying Earth tone
- [ ] **Dialogue Style:** NPC interactions use appropriate archaic language

## 🎭 Character-Specific Tests

### **Lord Valerius (Warrior)**
```python
# Test mighty deed
python3 dcc_judge.py --character dying_earth_noble.json --action mighty-deed --deed "Disarm with courtly flourish"

# Test crit with Warrior table
python3 dcc_judge.py --character dying_earth_noble.json --action roll-attack --target "Ancient Guardian"
```

### **Silk the Shadow-Dancer (Thief)**
```python
# Test thief skills
python3 dcc_judge.py --character dying_earth_thief.json --action sneak --difficulty 4

# Test backstab
python3 dcc_judge.py --character dying_earth_thief.json --action backstab --target "Unwary Guard"
```

### **Zephyrim the Last Geomancer (Wizard)**
```python
# Test spell with mercurial effect
python3 dcc_judge.py --character dying_earth_wizard.json --action cast-spell --spell "Magic Missile" --target "Crystal Golem"

# Test spell failure corruption
python3 dcc_judge.py --character dying_earth_wizard.json --action spell-failure --spell "Magic Missile"
```

### **Sister Solara (Cleric)**
```python
# Test turn undead
python3 dcc_judge.py --character dying_earth_cleric.json --action turn-undead --undead-type "Spectral Remnant"

# Test healing
python3 dcc_judge.py --character dying_earth_cleric.json --action heal --target dying_earth_noble.json --amount 3
```

## 🔧 Troubleshooting

### **Common Issues & Solutions:**

#### **Issue: Character files not loading**
```bash
# Check file permissions
ls -la /Users/chriscoon/ttrpg_gm/data/characters/

# Validate JSON format
python3 -m json.tool /Users/chriscoon/ttrpg_gm/data/characters/dying_earth_noble.json
```

#### **Issue: DCC Judge not responding**
```bash
# Check Python environment
python3 --version

# Check dependencies
pip3 list | grep -E "deepseek|openai|requests"

# Test basic functionality
python3 dcc_judge.py --help
```

#### **Issue: Literary style not applying**
```bash
# Check refinement system
python3 dcc_judge.py --test-refinement --text "Test description"

# Verify DeepSeek API connection
python3 dcc_judge.py --test-api
```

### **Performance Testing:**
```bash
# Test response time
time python3 dcc_judge.py --character dying_earth_noble.json --action roll --skill perception

# Test memory usage during gameplay
python3 dcc_judge.py --profile --duration 30
```

## 📊 Test Results Template

**Test Date:** _______________  
**Tester:** _______________  
**System Version:** _______________

### **Mechanics Test Results:**
- Spellburn: □ Pass □ Fail □ Partial  
- Corruption: □ Pass □ Fail □ Partial  
- Luck System: □ Pass □ Fail □ Partial  
- Mercurial Magic: □ Pass □ Fail □ Partial  
- Crit/Fumble Tables: □ Pass □ Fail □ Partial  
- Thief Skills: □ Pass □ Fail □ Partial  
- Turn Undead: □ Pass □ Fail □ Partial  
- Mighty Deeds: □ Pass □ Fail □ Partial  

### **Literary Style Results:**
- Dying Earth Prose: □ Excellent □ Good □ Fair □ Poor  
- Character Voice: □ Excellent □ Good □ Fair □ Poor  
- Atmospheric Descriptions: □ Excellent □ Good □ Fair □ Poor  
- Dialogue Style: □ Excellent □ Good □ Fair □ Poor  

### **Performance Results:**
- Response Time: □ Fast (<2s) □ Moderate (2-5s) □ Slow (>5s)  
- Memory Usage: □ Low □ Moderate □ High  
- System Stability: □ Stable □ Occasional Issues □ Unstable  

### **Issues Found:**
1. _______________
2. _______________
3. _______________

### **Recommendations:**
1. _______________
2. _______________
3. _______________

## 🎯 Next Steps After Testing

### **If All Tests Pass:**
1. **Begin Campaign:** Start with Dying Earth adventure #1
2. **Invite Players:** Share character sheets with potential players
3. **Schedule Session:** Set up first gameplay session
4. **Document Experience:** Record gameplay for system refinement

### **If Issues Found:**
1. **Prioritize Fixes:** Address critical mechanics first
2. **Test Iteratively:** Fix one issue, retest, continue
3. **Update Documentation:** Note fixes in system docs
4. **Re-test:** Run full test suite after fixes

### **System Enhancement Opportunities:**
1. **Add More DCC Tables:** Extract additional tables from rulebook
2. **Expand Character Options:** Create more pre-generated characters
3. **Enhance Literary Style:** Add more Dying Earth author variations
4. **Improve Performance:** Optimize response times and memory usage

## 📞 Support & Feedback

**For Issues:**
1. Check troubleshooting section above
2. Review system logs: `/tmp/ttrpg_gm_*.log`
3. Test individual components separately

**For Feedback:**
1. Update test results template
2. Note literary style impressions
3. Suggest mechanical improvements
4. Report performance observations

**Contact:** System will auto-document issues in daily memory files

---

**Ready for Adventure:** The Dying Earth awaits with 11 prepared adventures and 4 thematic characters. Begin your journey into the fading sunset of a dying world.

*"In the twilight of the sun, all glory fades to shadow, and only courage remains to light the final hours."*