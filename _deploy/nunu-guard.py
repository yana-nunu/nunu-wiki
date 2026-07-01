#!/usr/bin/env python3
"""NUNU PreToolUse guard — run unattended for Yana's marketing work without stalling on approvals,
while dangerous edges stay HARD-BLOCKED (exit code 2).

Adapted from MOMO's guard, but TIGHTER: NUNU is operated by a non-technical user (Yana), so there is
NO interactive "ask-a-human" tier — anything not clearly safe is BLOCKED (flag Eli) rather than
prompting. Eli can override a soft block during a manual session by appending  #ELI_OK  (never a
hard-block, never an unknown command).

Wired into /Users/nunu/nunu/.claude/settings.local.json -> hooks.PreToolUse (matcher "*").

Tiers:
  AUTO-APPROVE  reads; edits/writes inside /Users/nunu; build/test/dev + local-git; web; Discord
                comms; Claude Design tools; read-only MCP; git push to NUNU's own wiki.
  HARD-BLOCK    spend money; macOS/system settings; destructive deletes outside the work dir;
                curl|bash RCE; money MCP. NEVER bypassable.
  BLOCK         install software; publish/deploy (except own-wiki push); writes outside the work
                dir; any command whose leading tool isn't on the allowlist. Fail-closed. Eli-override
                via #ELI_OK for the soft ones only.
"""
import sys, json, os, re, shlex, datetime

WORK = "/Users/nunu"
WIKI = "/users/nunu/nunu/wiki"  # lowercased; NUNU's own wiki repo — git push here is auto-approved
SAFE_PREFIXES = (WORK, "/tmp", "/private/tmp", "/var/folders")

DEV_ALLOW = {
    "bun", "bunx", "npm", "npx", "node", "pnpm", "yarn", "deno",
    "python3", "python", "prisma", "next", "tsc", "eslint", "jest", "vitest", "playwright",
    "psql", "git", "gh", "ls", "cat", "head", "tail", "grep", "egrep", "fgrep", "rg",
    "echo", "printf", "mkdir", "touch", "cp", "mv", "chmod", "ln", "pwd", "cd", "sleep",
    "wc", "sort", "uniq", "awk", "sed", "jq", "which", "type", "ps", "pgrep",
    "df", "du", "date", "env", "true", "false", "test", "open", "curl",
    "tee", "basename", "dirname", "realpath", "readlink", "stat", "diff", "tr", "cut", "find", "wait", "time",
}
SYS_SETTINGS = {"defaults", "systemsetup", "networksetup", "pmset", "csrutil", "nvram",
                "spctl", "scutil", "dscl", "fdesetup", "softwareupdate", "osascript"}
PKG = {"brew", "port", "pip", "pip3", "pipx", "cargo", "go", "gem"}
CATASTROPHIC = re.compile(r"rm\s+-[rf]{1,2}\s+(/|~|\$HOME)(\s|/|$)|:\(\)\s*\{|mkfs|dd\s+if=.*of=/dev/|>\s*/dev/sd")
RCE_PIPE = re.compile(r"\b(curl|wget|fetch)\b[^|]*\|\s*(sudo\s+)?(bash|sh|zsh|dash|ksh)\b", re.I)
MONEY = re.compile(r"\b(stripe|paypal|braintree|checkout\.session|--billing|purchase|buy-)\b", re.I)
MCP_MONEY = re.compile(r"pay(ment|out)?|purchase|billing|charge|invoice|checkout|create.?order|subscribe", re.I)
MCP_PUBLISH = re.compile(r"publish|deploy|make.?public|send[_-]?(message|mail|email)", re.I)
MCP_COMMS_OK = re.compile(r"discord__(reply|react|edit_message|fetch_messages|download_attachment)", re.I)
MCP_DESIGN_OK = re.compile(r"mcp__claude_design__", re.I)  # NUNU's core design toolset
MCP_READ = re.compile(r"(get|list|search|read|fetch|download|resolve|view|thumbnail|content|pages|formats|describe|help|find|export|render|preview)", re.I)
SUBAGENT_ALLOW = {"WebSearch", "WebFetch", "ToolSearch", "Read", "Glob", "Grep", "LS",
                  "NotebookRead", "TodoWrite", "BashOutput"}
PROTECTED_FILES = {
    "/Users/nunu/nunu/ops/nunu-guard.py",
    "/Users/nunu/nunu/.claude/settings.local.json",
    "/Users/nunu/nunu/.claude/settings.json",
}
PROTECTED_BASENAMES = ("nunu-guard.py", "settings.local.json", "settings.json")

# Decision logging — every allow/block written to a log so we can tune the allow-list to REAL usage
# (add what got wrongly blocked, strip what's never used) before locking the guard down. Fails silently.
LOG_PATH = "/Users/nunu/nunu/ops/logs/guard.log"
TOOL = "?"


def _log(verdict, reason):
    try:
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        with open(LOG_PATH, "a") as f:
            f.write(f"{ts} {verdict:5} {TOOL} :: {reason}\n")
    except Exception:
        pass


def allow(reason):
    _log("ALLOW", reason)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
          "permissionDecision": "allow", "permissionDecisionReason": reason}}))
    sys.exit(0)


def block(reason):
    _log("BLOCK", reason)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
          "permissionDecision": "deny", "permissionDecisionReason": reason}}))
    sys.stderr.write(reason + "\n")
    sys.exit(2)


def subcommands(cmd):
    try:
        lex = shlex.shlex(cmd, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        toks = list(lex)
    except Exception:
        toks = cmd.split()
    subs, cur = [], []
    for t in toks:
        if t in (";", "&&", "||", "|", "&", "\n"):
            if cur:
                subs.append(cur); cur = []
        else:
            cur.append(t)
    if cur:
        subs.append(cur)
    return subs


def analyse_tokens(toks):
    """Return ('hard'|'block'|'dev', reason) for one sub-command."""
    i = 0
    while i < len(toks) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[i]):
        i += 1
    toks = toks[i:]
    if not toks:
        return ("dev", "")
    cmd = os.path.basename(toks[0].strip("(){}"))
    args = [a.lower() for a in toks[1:]]
    joined = " ".join(toks)
    jlow = joined.lower()

    if cmd == "sudo":
        return ("hard", "sudo / privilege escalation.")
    if cmd in SYS_SETTINGS:
        return ("hard", "macOS / system-settings change.")
    if cmd == "launchctl" and re.search(r"/System/|/Library/", joined):
        return ("hard", "system-level launchd change.")
    if cmd == "rm":
        for t in re.findall(r"(?<!\S)(~|\$HOME|/[^\s'\"]*)", joined):
            tt = os.path.expanduser(t.replace("$HOME", "~"))
            if t in ("~", "$HOME") or (tt.startswith("/") and not tt.startswith(SAFE_PREFIXES)):
                return ("hard", f"destructive delete outside the work dir ({t}).")
        return ("dev", "")
    if cmd in ("curl", "wget"):
        upflags = {"-d", "--data", "--data-binary", "--data-raw", "--data-urlencode", "-F", "--form",
                   "-T", "--upload-file", "--post-data", "--post-file"}
        if any(a in upflags for a in args) or any(a in ("-x", "--request") for a in args):
            return ("block", "curl/wget sending data outward — blocked (flag Eli if genuinely needed).")
    if cmd in PKG and ("install" in args or "add" in args):
        return ("block", "installing software — blocked (NUNU shouldn't need to; flag Eli).")
    if cmd == "gh" and args[:2] == ["extension", "install"]:
        return ("block", "installing a gh extension — blocked (flag Eli).")
    # git push: auto-approve ONLY to NUNU's own wiki; block any other push.
    if cmd == "git" and "push" in args:
        if WIKI in jlow:
            return ("dev", "")
        return ("block", "git push outside NUNU's own wiki — blocked (flag Eli).")
    if cmd in ("vercel", "netlify", "ngrok", "cloudflared"):
        return ("hard", "deploy / public tunnel.")
    if cmd == "dropdb":
        return ("hard", "dropping a database.")
    if cmd in DEV_ALLOW:
        return ("dev", "")
    return ("block", f"'{cmd}' isn't on the allowlist — blocked (flag Eli to add it).")


def _targets_protected(cmd):
    for b in PROTECTED_BASENAMES:
        if b not in cmd:
            continue
        eb = re.escape(b)
        if re.search(r">>?\s*[\'\"]?[^\s\'\"|&]*" + eb, cmd):
            return True
        if re.search(r"\b(cp|mv|rm|ln|tee|dd|truncate|chmod|chflags|chown|install)\b[^|;&]*" + eb, cmd):
            return True
        if re.search(r"\bsed\b[^|;&]*-i[^|;&]*" + eb, cmd):
            return True
    return False


def main():
    global TOOL
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    tool = data.get("tool_name", "")
    TOOL = tool or "?"
    inp = data.get("tool_input", {}) or {}

    if tool == "AskUserQuestion":
        block("Interactive option menu is disabled — reply to Yana in plain text via Discord.")

    if data.get("agent_id"):
        if tool in SUBAGENT_ALLOW or (tool.startswith("mcp__") and (MCP_READ.search(tool) or MCP_DESIGN_OK.search(tool)) and not MCP_MONEY.search(tool) and not MCP_PUBLISH.search(tool)):
            allow("subagent: web/read/design tool — auto-approved")
        block(f"SUBAGENT-BLOCKED: '{tool}' not permitted for subagents.")

    if tool.startswith("mcp__"):
        if MCP_MONEY.search(tool):
            block("HARD-BLOCK: an MCP action that looks like spending money. Never.")
        if MCP_COMMS_OK.search(tool):
            allow("Discord comms — auto-approved")
        if MCP_DESIGN_OK.search(tool):
            allow("Claude Design tool — auto-approved (NUNU's core toolset)")
        if MCP_PUBLISH.search(tool):
            block("BLOCK: an MCP action that publishes / sends outward — blocked (Yana sends; flag Eli).")
        if MCP_READ.search(tool):
            allow("read-only MCP tool — auto-approved")
        block("BLOCK: unrecognised MCP tool '" + tool + "' — fail-closed (flag Eli if needed).")

    if tool in ("WebFetch", "WebSearch"):
        allow("web research — auto-approved")

    SAFE_TOOLS = {"Read", "Glob", "Grep", "LS", "NotebookRead", "TodoWrite", "TaskCreate",
                  "TaskUpdate", "TaskList", "TaskGet", "BashOutput", "ToolSearch"}
    if tool in SAFE_TOOLS:
        allow("read-only tool — auto-approved")

    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        p = inp.get("file_path") or inp.get("notebook_path") or ""
        ap = os.path.abspath(p) if p else ""
        if ap in PROTECTED_FILES:
            block("HARD-BLOCK: refusing to modify NUNU's own guard / settings. Changes require Eli (sudo).")
        if ap.startswith(SAFE_PREFIXES):
            allow("edit/write inside work dir — auto-approved")
        block(f"BLOCK: writing OUTSIDE /Users/nunu ({p}) — blocked (flag Eli).")

    if tool == "Bash":
        cmd = inp.get("command", "") or ""
        if _targets_protected(cmd):
            block("HARD-BLOCK: refusing to modify NUNU's guard / settings via shell — self-disarm. Requires Eli (sudo).")
        if CATASTROPHIC.search(cmd):
            block("HARD-BLOCK: catastrophic command.")
        if RCE_PIPE.search(cmd):
            block("HARD-BLOCK: piping remote content into a shell (curl|bash RCE).")
        if MONEY.search(cmd):
            block("HARD-BLOCK: looks like spending money. Never.")

        verdicts = [analyse_tokens(t) for t in subcommands(cmd)] or [("dev", "")]
        for kind, reason in verdicts:
            if kind == "hard":
                block("HARD-BLOCK: " + reason)
        marker = "#eli_ok" in cmd.lower()
        if not marker:
            for kind, reason in verdicts:
                if kind == "block":
                    block("BLOCK: " + reason)
        allow("build/test/dev/local command — auto-approved")

    allow("unrecognised non-executing tool — auto-approved")


if __name__ == "__main__":
    main()
