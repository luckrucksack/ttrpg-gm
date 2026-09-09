#!/usr/bin/env bash
# bridge/check.sh — prove the Foundry MCP bridge actually works end to end.
#
# Checks, in order:
#   1. Foundry VTT answers on its HTTP port
#   2. MCP_FOUNDRY_PASSWORD is present in the profile .env
#   3. foundryvtt-mcp starts, authenticates, and registers tools (the real path)
#
# Exit 0 = the GM Bot will see mcp_foundry_* tools. Anything else = it will not.
#
# Usage: bash bridge/check.sh [--list]
#   --list  also print every registered tool name

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${HERMES_PROFILE_ENV:-$HOME/.hermes/profiles/ttrpg/.env}"
FOUNDRY_URL="${FOUNDRY_URL:-http://localhost:30000}"
FOUNDRY_USERNAME="${FOUNDRY_USERNAME:-mcp-api}"
MCP_PACKAGE="${MCP_PACKAGE:-foundryvtt-mcp@1.5.2}"

# npx lives in a few common places depending on how node was installed.
for d in "$HOME/.local/bin" /opt/homebrew/bin /usr/local/bin; do
  [ -d "$d" ] && PATH="$d:$PATH"
done
export PATH

pass() { printf '  \033[32mPASS\033[0m %s\n' "$1"; }
fail() { printf '  \033[31mFAIL\033[0m %s\n' "$1"; }
info() { printf '       %s\n' "$1"; }

echo "Foundry MCP bridge check"
echo "  url:      $FOUNDRY_URL"
echo "  user:     $FOUNDRY_USERNAME"
echo "  env file: $ENV_FILE"
echo

# --- 1. Foundry reachable -----------------------------------------------------
code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 "$FOUNDRY_URL/" 2>/dev/null || echo 000)"
if [ "$code" = "000" ]; then
  fail "Foundry not reachable at $FOUNDRY_URL"
  info "start it: launchctl kickstart -k gui/$(id -u)/com.hermes.foundryvtt"
  exit 1
fi
pass "Foundry responds (HTTP $code)"

# --- 2. Secret present --------------------------------------------------------
if [ ! -f "$ENV_FILE" ]; then
  fail "profile .env not found: $ENV_FILE"
  exit 1
fi
if ! grep -q '^MCP_FOUNDRY_PASSWORD=.\+' "$ENV_FILE"; then
  fail "MCP_FOUNDRY_PASSWORD missing or empty in $ENV_FILE"
  info "the MCP server will be launched with a literal \${MCP_FOUNDRY_PASSWORD} and auth will fail"
  exit 1
fi
pass "MCP_FOUNDRY_PASSWORD present"

# --- 3. Real launch: does the server register tools? --------------------------
FOUNDRY_URL="$FOUNDRY_URL" \
FOUNDRY_USERNAME="$FOUNDRY_USERNAME" \
MCP_PACKAGE="$MCP_PACKAGE" \
ENV_FILE="$ENV_FILE" \
BRIDGE_CWD="$HERE" \
python3 - "$@" <<'PY'
import json, os, re, subprocess, sys, select, tempfile, time

url = os.environ["FOUNDRY_URL"]
bridge_cwd = os.environ["BRIDGE_CWD"]
user = os.environ["FOUNDRY_USERNAME"]
pkg = os.environ["MCP_PACKAGE"]
env_file = os.environ["ENV_FILE"]
show_list = "--list" in sys.argv

pw = None
with open(env_file) as fh:
    for line in fh:
        m = re.match(r"^MCP_FOUNDRY_PASSWORD=(.*)$", line.rstrip("\n"))
        if m:
            pw = m.group(1).strip().strip('"').strip("'")
if not pw:
    print("  FAIL could not read MCP_FOUNDRY_PASSWORD")
    sys.exit(1)

env = dict(os.environ)
env.update({
    "FOUNDRY_URL": url,
    "FOUNDRY_USERNAME": user,
    "FOUNDRY_PASSWORD": pw,
    "FOUNDRY_WRITE_ENABLED": "true",
})

# The server calls dotenv.config(), which reads .env from its *working
# directory*. A stray .env there (e.g. LOG_LEVEL=INFO) kills it at startup
# with an opaque "Connection closed", so pin cwd to the bridge dir --
# exactly what mcp_servers.foundry does in the profile config.
errlog = tempfile.NamedTemporaryFile("w+", prefix="bridge-check-", suffix=".log", delete=False)
err_path = errlog.name
proc = subprocess.Popen(
    ["npx", "-y", pkg],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errlog,
    text=True, bufsize=1, env=env, cwd=bridge_cwd,
)

def dump_stderr():
    """Print the server's own error output -- the actual reason it died."""
    try:
        errlog.flush()
        with open(err_path) as fh:
            lines = [l.rstrip() for l in fh if l.strip()]
    except OSError:
        lines = []
    if lines:
        print("       --- server stderr (last 8) ---")
        for line in lines[-8:]:
            print(f"       {line}")

def send(obj):
    proc.stdin.write(json.dumps(obj) + "\n")
    proc.stdin.flush()

def read_until(pred, timeout=90):
    """Read newline-delimited JSON-RPC until pred(msg) is true or timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        r, _, _ = select.select([proc.stdout], [], [], 1.0)
        if not r:
            if proc.poll() is not None:
                return None
            continue
        line = proc.stdout.readline()
        if not line:
            return None
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if pred(msg):
            return msg
    return None

send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
      "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                 "clientInfo": {"name": "bridge-check", "version": "1.0"}}})
init = read_until(lambda m: m.get("id") == 1)
if not init or "result" not in init:
    print("  FAIL MCP server did not complete the initialize handshake")
    print("       it exits immediately when Foundry is unreachable, the")
    print("       credentials are wrong, or its cwd holds a bad .env")
    proc.kill()
    dump_stderr()
    sys.exit(1)

send({"jsonrpc": "2.0", "method": "notifications/initialized"})
send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
tl = read_until(lambda m: m.get("id") == 2)
proc.kill()
if not tl or "result" not in tl:
    print("  FAIL no tool list returned")
    dump_stderr()
    sys.exit(1)

tools = [t["name"] for t in tl["result"].get("tools", [])]
if not tools:
    print("  FAIL server started but registered zero tools")
    sys.exit(1)

print(f"  PASS bridge live — {len(tools)} tools registered as mcp_foundry_*")
if show_list:
    for name in sorted(tools):
        print(f"       mcp_foundry_{name}")
PY
status=$?

echo
if [ $status -eq 0 ]; then
  echo "Bridge OK — the GM Bot will see Foundry tools."
else
  echo "Bridge DOWN — the GM Bot will have no mcp_foundry_* tools."
fi
exit $status
