#!/usr/bin/env bash
# setup.sh — One-time setup for the AI-GM system
# Run from the ttrpg_gm repo root.
#
# Prerequisites:
#   - Foundry VTT running on localhost:30000
#   - npm/node installed
#   - Hermes Agent with ttrpg profile configured

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TTRPG_PROFILE="${HOME}/.hermes/profiles/ttrpg"

echo "=== TTRPG AI-GM Setup ==="
echo ""

# 1. Install MCP server
if ! npx -y foundryvtt-mcp --version 2>/dev/null; then
  echo "[1/4] Installing foundryvtt-mcp..."
  npm install -g foundryvtt-mcp 2>/dev/null || true
else
  echo "[1/4] foundryvtt-mcp already available"
fi

# 2. Test Foundry connectivity
echo -n "[2/4] Testing Foundry connectivity..."
if curl -sf http://localhost:30000/ > /dev/null 2>&1; then
  echo " OK"
else
  echo " FAIL — is Foundry running on :30000?"
  exit 1
fi

# 3. Check MCP user exists in Foundry
echo "[3/4] Checking for MCP API user..."
echo "  → Create a user named 'mcp-api' with role 'Assistant GM'"
echo "  → In Foundry: Configuration → User Management → Create User"
echo "  → Set a strong password and note it"
echo ""

# 4. Configure MCP in ttrpg profile
echo "[4/4] Configuring Hermes MCP server..."
CONFIG="${TTRPG_PROFILE}/config.yaml"

if grep -q "foundryvtt-mcp" "${CONFIG}" 2>/dev/null; then
  echo "  → MCP server already configured in ttrpg profile"
else
  echo "  → Add the following to ${CONFIG} under mcp_servers:"
  echo ""
  cat << 'CONF'
  foundry:
    command: "npx"
    args: ["-y", "foundryvtt-mcp"]
    env:
      FOUNDRY_URL: "http://localhost:30000"
      FOUNDRY_USERNAME: "mcp-api"
      FOUNDRY_PASSWORD: "<your-password>"
      FOUNDRY_WRITE_ENABLED: "true"
    timeout: 120
    connect_timeout: 30
CONF
fi

echo ""
echo "=== Setup instructions ==="
echo ""
echo "1. Create 'mcp-api' user in Foundry (Assistant GM role)"
echo "2. Add MCP config block to ~/.hermes/profiles/ttrpg/config.yaml"
echo "3. Restart Hermes ttrpg profile: hermes -p ttrpg"
echo "4. Verify MCP connection: python pipeline/import_foundry.py status"
echo ""
echo "Your adventure PDFs go into campaigns/ dir."
echo "Then: python pipeline/ingest.py campaigns/my-adventure.pdf"