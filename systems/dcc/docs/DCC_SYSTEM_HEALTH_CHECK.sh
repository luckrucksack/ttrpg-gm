#!/bin/bash

# DCC System Health Check Script
# Created: March 22, 2026
# Purpose: Monitor and maintain DCC Judge system health

echo "================================================"
echo "DCC SYSTEM HEALTH CHECK"
echo "================================================"
echo "Date: $(date)"
echo "System: Dungeon Crawl Classics Judge + Dying Earth"
echo "Version: v1.0 (Initial Release)"
echo "================================================"
echo ""

# Configuration
DCC_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
LOG_FILE="/tmp/dcc_health_check_$(date +%Y%m%d_%H%M%S).log"
CHECK_RESULTS=()

# Function to log results
log_result() {
    local status=$1
    local message=$2
    local category=$3
    
    CHECK_RESULTS+=("$status|$category|$message")
    
    case $status in
        "✅") echo "  $status $message" ;;
        "⚠️") echo "  $status $message" ;;
        "❌") echo "  $status $message" ;;
        *) echo "  $status $message" ;;
    esac
}

# Function to run check
run_check() {
    local category=$1
    local check_name=$2
    local command=$3
    local success_pattern=$4
    
    echo ""
    echo "🔍 $category: $check_name"
    
    if eval "$command" 2>/dev/null | grep -q "$success_pattern"; then
        log_result "✅" "$check_name: PASSED" "$category"
        return 0
    else
        log_result "❌" "$check_name: FAILED" "$category"
        return 1
    fi
}

echo "Starting comprehensive DCC system health check..."
echo ""

# ================================================
# 1. SYSTEM PREREQUISITES CHECK
# ================================================
echo "📋 1. SYSTEM PREREQUISITES"

# Check Python 3
if python3 --version 2>/dev/null | grep -q "Python 3"; then
    PYTHON_VERSION=$(python3 --version 2>/dev/null)
    log_result "✅" "Python 3: $PYTHON_VERSION" "Prerequisites"
else
    log_result "❌" "Python 3: NOT FOUND" "Prerequisites"
fi

# Check directory
if [ -d "$DCC_DIR" ]; then
    log_result "✅" "DCC directory exists: $DCC_DIR" "Prerequisites"
else
    log_result "❌" "DCC directory missing: $DCC_DIR" "Prerequisites"
fi

# ================================================
# 2. CORE FILES CHECK
# ================================================
echo ""
echo "📋 2. CORE FILES"

# Check DCC Judge main file
if [ -f "$DCC_DIR/systems/dcc/judge.py" ]; then
    log_result "✅" "DCC Judge main file exists" "Core Files"
else
    log_result "❌" "DCC Judge main file missing" "Core Files"
fi

# Check character files
CHAR_FILES=(
    "dying_earth_noble.json"
    "dying_earth_thief.json"
    "dying_earth_wizard.json"
    "dying_earth_cleric.json"
)

CHAR_COUNT=0
for char in "${CHAR_FILES[@]}"; do
    if [ -f "$DCC_DIR/campaigns/dying_earth/characters/$char" ]; then
        CHAR_COUNT=$((CHAR_COUNT + 1))
    fi
done

if [ $CHAR_COUNT -eq 4 ]; then
    log_result "✅" "All 4 character files exist" "Core Files"
elif [ $CHAR_COUNT -gt 0 ]; then
    log_result "⚠️" "Only $CHAR_COUNT/4 character files exist" "Core Files"
else
    log_result "❌" "No character files found" "Core Files"
fi

# ================================================
# 3. DOCUMENTATION CHECK
# ================================================
echo ""
echo "📋 3. DOCUMENTATION"

DOC_FILES=(
    "DCC_QUICK_START_GUIDE.md"
    "DCC_SYSTEM_VALIDATION_REPORT.md"
    "DCC_SYSTEM_ROADMAP.md"
    "DCC_SYSTEM_DELIVERY_SUMMARY.md"
)

DOC_COUNT=0
for doc in "${DOC_FILES[@]}"; do
    if [ -f "$DCC_DIR/$doc" ]; then
        DOC_COUNT=$((DOC_COUNT + 1))
    fi
done

if [ $DOC_COUNT -eq 4 ]; then
    log_result "✅" "All 4 documentation files exist" "Documentation"
else
    log_result "⚠️" "Only $DOC_COUNT/4 documentation files exist" "Documentation"
fi

# ================================================
# 4. SCRIPT FUNCTIONALITY CHECK
# ================================================
echo ""
echo "📋 4. SCRIPTS & AUTOMATION"

# Check test script
if [ -f "$DCC_DIR/test_dcc_system.sh" ]; then
    if [ -x "$DCC_DIR/test_dcc_system.sh" ]; then
        log_result "✅" "Test script exists and is executable" "Scripts"
    else
        log_result "⚠️" "Test script exists but not executable" "Scripts"
    fi
else
    log_result "❌" "Test script missing" "Scripts"
fi

# Check adventure runner
if [ -f "$DCC_DIR/run_mechanics_test.sh" ]; then
    if [ -x "$DCC_DIR/run_mechanics_test.sh" ]; then
        log_result "✅" "Adventure runner exists and is executable" "Scripts"
    else
        log_result "⚠️" "Adventure runner exists but not executable" "Scripts"
    fi
else
    log_result "❌" "Adventure runner missing" "Scripts"
fi

# ================================================
# 5. ADVENTURE CONTENT CHECK
# ================================================
echo ""
echo "📋 5. ADVENTURE CONTENT"

# Check adventure file
if [ -f "$DCC_DIR/campaigns/dying_earth/adventures/dcc_mechanics_test_adventure.md" ]; then
    ADVENTURE_SIZE=$(wc -l < "$DCC_DIR/campaigns/dying_earth/adventures/dcc_mechanics_test_adventure.md")
    if [ $ADVENTURE_SIZE -gt 100 ]; then
        log_result "✅" "Adventure file exists ($ADVENTURE_SIZE lines)" "Adventure"
    else
        log_result "⚠️" "Adventure file exists but very small ($ADVENTURE_SIZE lines)" "Adventure"
    fi
else
    log_result "❌" "Adventure file missing" "Adventure"
fi

# ================================================
# 6. SYSTEM INTEGRATION CHECK
# ================================================
echo ""
echo "📋 6. SYSTEM INTEGRATION"

# Check if DCC Judge can be imported
cd "$DCC_DIR" 2>/dev/null
if python3 -c "import sys; sys.path.insert(0, '.'); exec(open('systems/dcc/judge.py').read())" 2>/dev/null; then
    log_result "✅" "DCC Judge Python code loads without errors" "Integration"
else
    log_result "❌" "DCC Judge Python code has errors" "Integration"
fi

# Check character JSON validity
JSON_ERRORS=0
for char in "${CHAR_FILES[@]}"; do
    if [ -f "$DCC_DIR/campaigns/dying_earth/characters/$char" ]; then
        if ! python3 -m json.tool "$DCC_DIR/campaigns/dying_earth/characters/$char" >/dev/null 2>&1; then
            JSON_ERRORS=$((JSON_ERRORS + 1))
        fi
    fi
done

if [ $JSON_ERRORS -eq 0 ]; then
    log_result "✅" "All character JSON files are valid" "Integration"
else
    log_result "❌" "$JSON_ERRORS character JSON files have errors" "Integration"
fi

# ================================================
# 7. PERFORMANCE CHECK
# ================================================
echo ""
echo "📋 7. PERFORMANCE"

# Check response time (basic)
START_TIME=$(date +%s%N)
cd "$DCC_DIR" 2>/dev/null
python3 -c "import sys; sys.path.insert(0, '.'); exec(open('systems/dcc/judge.py').read())" --help 2>&1 >/dev/null
END_TIME=$(date +%s%N)
RESPONSE_MS=$(( (END_TIME - START_TIME) / 1000000 ))

if [ $RESPONSE_MS -lt 1000 ]; then
    log_result "✅" "Basic response time: ${RESPONSE_MS}ms (Good)" "Performance"
elif [ $RESPONSE_MS -lt 3000 ]; then
    log_result "⚠️" "Basic response time: ${RESPONSE_MS}ms (Acceptable)" "Performance"
else
    log_result "❌" "Basic response time: ${RESPONSE_MS}ms (Slow)" "Performance"
fi

# Check file sizes
TOTAL_SIZE=$(find "$DCC_DIR" -name "*.json" -o -name "*.md" -o -name "*.sh" 2>/dev/null | grep -E "(dying_earth|DCC|test_|run_)" | xargs ls -la 2>/dev/null | awk '{sum+=$5} END {print sum}')
if [ $TOTAL_SIZE -gt 50000 ]; then
    log_result "✅" "Total system size: $(($TOTAL_SIZE/1024))KB (Good)" "Performance"
else
    log_result "⚠️" "Total system size: $(($TOTAL_SIZE/1024))KB (Small)" "Performance"
fi

# ================================================
# 8. SECURITY CHECK
# ================================================
echo ""
echo "📋 8. SECURITY"

# Check file permissions
INSECURE_FILES=0
find "$DCC_DIR" -name "*.sh" -type f 2>/dev/null | while read file; do
    if [ -x "$file" ] && [ "$(stat -f %p "$file" 2>/dev/null | cut -c 4)" != "0" ]; then
        INSECURE_FILES=$((INSECURE_FILES + 1))
    fi
done

if [ $INSECURE_FILES -eq 0 ]; then
    log_result "✅" "Script file permissions are secure" "Security"
else
    log_result "⚠️" "$INSECURE_FILES script files have world permissions" "Security"
fi

# Check for sensitive data in JSON files
SENSITIVE_DATA=0
for char in "${CHAR_FILES[@]}"; do
    if [ -f "$DCC_DIR/campaigns/dying_earth/characters/$char" ]; then
        if grep -q -i "password\\|secret\\|key\\|token" "$DCC_DIR/campaigns/dying_earth/characters/$char"; then
            SENSITIVE_DATA=$((SENSITIVE_DATA + 1))
        fi
    fi
done

if [ $SENSITIVE_DATA -eq 0 ]; then
    log_result "✅" "No sensitive data found in character files" "Security"
else
    log_result "❌" "Sensitive data found in $SENSITIVE_DATA character files" "Security"
fi

# ================================================
# 9. MAINTENANCE RECOMMENDATIONS
# ================================================
echo ""
echo "📋 9. MAINTENANCE RECOMMENDATIONS"

# Count total checks
TOTAL_CHECKS=${#CHECK_RESULTS[@]}
PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0

for result in "${CHECK_RESULTS[@]}"; do
    status=$(echo "$result" | cut -d'|' -f1)
    case $status in
        "✅") PASS_COUNT=$((PASS_COUNT + 1)) ;;
        "⚠️") WARN_COUNT=$((WARN_COUNT + 1)) ;;
        "❌") FAIL_COUNT=$((FAIL_COUNT + 1)) ;;
    esac
done

# Generate summary
echo ""
echo "================================================"
echo "HEALTH CHECK SUMMARY"
echo "================================================"
echo "Total Checks: $TOTAL_CHECKS"
echo "✅ Passed: $PASS_COUNT"
echo "⚠️ Warnings: $WARN_COUNT"
echo "❌ Failed: $FAIL_COUNT"
echo ""

# Calculate health score
if [ $TOTAL_CHECKS -gt 0 ]; then
    HEALTH_SCORE=$(( (PASS_COUNT * 100) / TOTAL_CHECKS ))
else
    HEALTH_SCORE=0
fi

echo "Overall Health Score: $HEALTH_SCORE%"
echo ""

# Health status
if [ $HEALTH_SCORE -ge 90 ]; then
    echo "🏥 SYSTEM HEALTH: EXCELLENT"
    echo "   The DCC system is in excellent condition."
elif [ $HEALTH_SCORE -ge 70 ]; then
    echo "🏥 SYSTEM HEALTH: GOOD"
    echo "   The DCC system is in good condition with minor issues."
elif [ $HEALTH_SCORE -ge 50 ]; then
    echo "🏥 SYSTEM HEALTH: FAIR"
    echo "   The DCC system has several issues that need attention."
else
    echo "🏥 SYSTEM HEALTH: POOR"
    echo "   The DCC system has significant issues requiring immediate attention."
fi

echo ""

# Generate recommendations
echo "🔧 RECOMMENDED ACTIONS:"
echo ""

if [ $FAIL_COUNT -gt 0 ]; then
    echo "1. ❌ FIX CRITICAL ISSUES ($FAIL_COUNT found):"
    for result in "${CHECK_RESULTS[@]}"; do
        status=$(echo "$result" | cut -d'|' -f1)
        message=$(echo "$result" | cut -d'|' -f3)
        if [ "$status" = "❌" ]; then
            echo "   • $message"
        fi
    done
    echo ""
fi

if [ $WARN_COUNT -gt 0 ]; then
    echo "2. ⚠️ ADDRESS WARNINGS ($WARN_COUNT found):"
    for result in "${CHECK_RESULTS[@]}"; do
        status=$(echo "$result" | cut -d'|' -f1)
        message=$(echo "$result" | cut -d'|' -f3)
        if [ "$status" = "⚠️" ]; then
            echo "   • $message"
        fi
    done
    echo ""
fi

# General maintenance recommendations
echo "3. 🛠️ REGULAR MAINTENANCE:"
echo "   • Run this health check weekly"
echo "   • Review DCC_SYSTEM_ROADMAP.md for evolution planning"
echo "   • Test system with ./test_dcc_system.sh monthly"
echo "   • Update documentation when making changes"
echo ""

# Performance recommendations
if [ $RESPONSE_MS -gt 1000 ]; then
    echo "4. ⚡ PERFORMANCE OPTIMIZATION:"
    echo "   • System response time is ${RESPONSE_MS}ms (consider optimization)"
    echo "   • Check API call efficiency in DCC Judge"
    echo "   • Consider caching frequent responses"
    echo ""
fi

# Security recommendations
if [ $INSECURE_FILES -gt 0 ] || [ $SENSITIVE_DATA -gt 0 ]; then
    echo "5. 🔒 SECURITY HARDENING:"
    if [ $INSECURE_FILES -gt 0 ]; then
        echo "   • Fix permissions on $INSECURE_FILES script files"
    fi
    if [ $SENSITIVE_DATA -gt 0 ]; then
        echo "   • Remove sensitive data from $SENSITIVE_DATA character files"
    fi
    echo ""
fi

# Next steps based on health
echo "6. 🚀 NEXT STEPS:"
if [ $HEALTH_SCORE -ge 90 ]; then
    echo "   • System is ready for production use"
    echo "   • Consider Phase 2 enhancements from roadmap"
    echo "   • Plan additional adventure content"
elif [ $HEALTH_SCORE -ge 70 ]; then
    echo "   • Address warnings before production use"
    echo "   • Run comprehensive testing"
    echo "   • Review Phase 1 bug fixes in roadmap"
else
    echo "   • Fix critical issues immediately"
    echo "   • Run detailed diagnostics"
    echo "   • Consider system restoration from backups"
fi
echo ""

# Log file information
echo "📝 Detailed results logged to: $LOG_FILE"
echo "   To view: cat $LOG_FILE"
echo