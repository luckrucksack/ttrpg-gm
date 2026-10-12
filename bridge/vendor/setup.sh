#!/usr/bin/env bash
# bridge/vendor/setup.sh — build the patched foundryvtt-mcp that the GM runs.
#
# Why this exists
# ---------------
# Upstream (1.5.2 and 1.5.3) hard-codes the journal page text limit at 500
# characters in `handleGetJournal`, so long journal pages — the NPC dossiers —
# reach the GM Bot truncated mid-sentence. This script vendors the pinned
# package, applies the local delta (limit becomes configurable via
# FOUNDRY_JOURNAL_TEXT_LIMIT, and page text is rendered readably), and keeps a
# pristine copy of the touched files for diffing.
#
# Usage:   bash bridge/vendor/setup.sh [version]      # default: 1.5.2
# Output:  bridge/vendor/foundryvtt-mcp/              # gitignored, regenerate any time
#          bridge/vendor/foundryvtt-mcp/dist.pristine/  # pre-patch copy, for `diff -u`
#
# Re-run after any version bump, then `bash bridge/check.sh`.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="${1:-1.5.2}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

for d in "$HOME/.local/bin" /opt/homebrew/bin /usr/local/bin; do
  [ -d "$d" ] && PATH="$d:$PATH"
done
export PATH

echo "vendoring foundryvtt-mcp@$VERSION"
( cd "$WORK" && npm pack "foundryvtt-mcp@$VERSION" --silent >/dev/null )
tar -xzf "$WORK/foundryvtt-mcp-$VERSION.tgz" -C "$WORK"

TARGET="$HERE/foundryvtt-mcp"
rm -rf "$TARGET"
mv "$WORK/package" "$TARGET"

# pre-patch copy of what we touch, for `diff -u`
cp "$TARGET/dist/tools/handlers/journals.js" "$TARGET/dist/tools/handlers/journals.js.pristine"
cp "$TARGET/dist/tools/definitions.js" "$TARGET/dist/tools/definitions.js.pristine"

python3 - "$TARGET" <<'PY'
import sys

target = sys.argv[1] + "/dist/tools/handlers/journals.js"
src = open(target).read()

def swap(text, old, new, label):
    n = text.count(old)
    assert n == 1, "expected 1 match for %s, found %d — upstream code changed; re-derive the patch" % (label, n)
    return text.replace(old, new)

# 1. the limit becomes an env knob (default 500 = upstream behavior)
src = swap(src,
    "            const content = p.text?.content\n",
    "            const limit = Number.parseInt(process.env.FOUNDRY_JOURNAL_TEXT_LIMIT ?? '', 10) || 500;\n"
    "            const content = p.text?.content\n",
    "limit const")

# 2. readable rendering: bullets and line breaks preserved, entities decoded
src = swap(src,
    "                ?.replace(/<[^>]+>/g, '')\n"
    "                .trim()\n"
    "                .slice(0, 500) || '';\n",
    "                ?.replace(/<li[^>]*>/gi, '\\n- ')\n"
    "                .replace(/<\\/li>|<\\/p>|<\\/h[1-6]>|<br\\s*\\/?>/gi, '\\n')\n"
    "                .replace(/<[^>]+>/g, '')\n"
    "                .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')\n"
    "                .replace(/&quot;/g, '\"').replace(/&#39;/g, \"'\")\n"
    "                .split('\\n').map((l) => l.trimEnd()).join('\\n')\n"
    "                .replace(/\\n{3,}/g, '\\n\\n').replace(/^\\n+|\\n+$/g, '')\n"
    "                .slice(0, limit) || '';\n",
    "content pipeline")

# 3. the truncation marker follows the configured limit
src = swap(src,
    "            return `### ${p.name}\\n${content}${content.length >= 500 ? '...' : ''}`;\n",
    "            return `### ${p.name}\\n${content}${content.length >= limit ? '...' : ''}`;\n",
    "truncation marker")

open(target, "w").write(src)

# 4. tool description reflects the new behavior (span-based: robust to quoting/escapes)
tdesc = sys.argv[1] + "/dist/tools/definitions.js"
txt = open(tdesc).read()
start = txt.find("Page bodies are HTML-stripped")
end = txt.find("so long pages come back partial.", start)
assert start != -1 and end != -1, "tool description not found — upstream wording changed; re-derive the patch"
end += len("so long pages come back partial.")
txt = txt[:start] + "Page bodies are rendered to plain text (bullets preserved) and each is truncated to its first FOUNDRY_JOURNAL_TEXT_LIMIT characters (default 500)." + txt[end:]
open(tdesc, "w").write(txt)

# 5. journal-mutations.js — add a delete handler (upstream ships create only)
jmut = sys.argv[1] + "/dist/tools/handlers/journal-mutations.js"
s = open(jmut).read()
assert "handleDeleteJournalEntry" not in s, "delete handler already present"
s = swap(s,
    "//# sourceMappingURL=journal-mutations.js.map",
    "\n/**\n"
    " * Handles deleting a journal entry by id.\n"
    " */\n"
    "export async function handleDeleteJournalEntry(args, foundryClient) {\n"
    "    const { journalId } = args;\n"
    "    if (!journalId || typeof journalId !== 'string') {\n"
    "        throw new McpError(ErrorCode.InvalidParams, 'journalId is required and must be a string');\n"
    "    }\n"
    "    return withToolError('delete journal entry', async () => {\n"
    "        await foundryClient.deleteJournalEntry(journalId);\n"
    "        return {\n"
    "            content: [\n"
    "                {\n"
    "                    type: 'text',\n"
    "                    text: `🗑️ **Journal Entry Deleted**\\n**ID:** ${journalId}`,\n"
    "                },\n"
    "            ],\n"
    "        };\n"
    "    });\n"
    "}\n"
    "//# sourceMappingURL=journal-mutations.js.map",
    "delete handler")
open(jmut, "w").write(s)

# 6. router.js — route the new tool
router = sys.argv[1] + "/dist/tools/router.js"
s = open(router).read()
s = swap(s,
    "import { handleCreateJournalEntry } from './handlers/journal-mutations.js';",
    "import { handleCreateJournalEntry, handleDeleteJournalEntry } from './handlers/journal-mutations.js';",
    "router import")
s = swap(s,
    "            return handleCreateJournalEntry(args, foundryClient);\n",
    "            return handleCreateJournalEntry(args, foundryClient);\n"
    "        case 'delete_journal_entry':\n"
    "            if (!('journalId' in args) || typeof args.journalId !== 'string') {\n"
    "                throw new Error('Missing required parameter: journalId');\n"
    "            }\n"
    "            return handleDeleteJournalEntry(args, foundryClient);\n",
    "router case")
open(router, "w").write(s)

# 7. client.js — the socket call (modifyDocument delete)
client = sys.argv[1] + "/dist/foundry/client.js"
s = open(client).read()
anchor = ("        const result = await this.modifyDocument('JournalEntry', 'create', {\n"
          "            data: [data],\n"
          "        });\n"
          "        return result[0];\n"
          "    }\n")
method = anchor + (
    "    /**\n"
    "     * Deletes a journal entry by id via the `modifyDocument` socket protocol.\n"
    "     * Local patch: upstream ships create/search/read only — there is no\n"
    "     * journal update or delete (an edit is delete + recreate).\n"
    "     *\n"
    "     * @param journalId - 16-char alphanumeric journal document id\n"
    "     * @returns the ids the server reports as deleted\n"
    "     */\n"
    "    async deleteJournalEntry(journalId) {\n"
    "        this.assertWriteable();\n"
    "        if (!FOUNDRY_ID_PATTERN.test(journalId)) {\n"
    "            throw new Error(`Invalid journalId format: ${journalId}`);\n"
    "        }\n"
    "        return this.modifyDocument('JournalEntry', 'delete', {\n"
    "            ids: [journalId],\n"
    "        });\n"
    "    }\n")
s = swap(s, anchor, method, "client delete method")
open(client, "w").write(s)

# 8. definitions.js — register the tool
tdef = sys.argv[1] + "/dist/tools/definitions.js"
s = open(tdef).read()
anchor = "            required: ['name', 'pages'],\n        },\n    },\n];\n"
newdef = ("            required: ['name', 'pages'],\n        },\n    },\n"
          "    {\n"
          "        name: 'delete_journal_entry',\n"
          "        description: 'Delete a journal entry by id. Destructive — there is no restore and no update path; an edit is delete + recreate. Use when: replacing an entry wholesale, or removing a mistaken duplicate. Do not use when: you only need to read or search - use get_journal / search_journals. ' +\n"
          "            WRITE_GATE,\n"
          "        inputSchema: {\n"
          "            type: 'object',\n"
          "            properties: {\n"
          "                journalId: {\n"
          "                    type: 'string',\n"
          "                    description: 'The ID of the journal entry to delete',\n"
          "                },\n"
          "            },\n"
          "            required: ['journalId'],\n"
          "        },\n"
          "    },\n"
          "];\n")
s = swap(s, anchor, newdef, "delete tool definition")
open(tdef, "w").write(s)

print("patched OK")
PY

echo
echo "installing runtime deps (npx would normally do this)"
( cd "$TARGET" && npm install --omit=dev --ignore-scripts --no-audit --no-fund --silent )

echo
echo "local delta:"
diff -u "$TARGET/dist/tools/handlers/journals.js.pristine" "$TARGET/dist/tools/handlers/journals.js" || true
echo
echo "next: bash bridge/check.sh   (should PASS and report the vendored server)"
