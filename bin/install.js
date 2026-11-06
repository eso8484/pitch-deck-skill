#!/usr/bin/env node
// Installs the pitch-deck skill for Claude Code.
//   npx pitch-deck-skill            -> ~/.claude/skills/pitch-deck (all projects)
//   npx pitch-deck-skill --project  -> ./.claude/skills/pitch-deck (this folder only)
//   npx pitch-deck-skill --uninstall [--project]
"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");

const SKILL = "pitch-deck";
const SRC = path.join(__dirname, "..", "skills", "pitch-deck");
const pkg = require("../package.json");
const args = new Set(process.argv.slice(2));

const c = (code) => (s) => (process.stdout.isTTY ? `\x1b[${code}m${s}\x1b[0m` : s);
const bold = c("1"), green = c("32"), yellow = c("33"), dim = c("2");

if (args.has("-h") || args.has("--help")) {
  console.log(`${bold("pitch-deck-skill")} ${pkg.version}

Installs the "${SKILL}" skill for Claude Code.

  npx pitch-deck-skill              install for all your projects (~/.claude/skills)
  npx pitch-deck-skill --project    install into this folder only (./.claude/skills)
  npx pitch-deck-skill --uninstall  remove it (add --project for the folder install)

After installing, open Claude Code and say "make me a pitch deck", or type /pitch-deck.`);
  process.exit(0);
}

const root = args.has("--project")
  ? path.join(process.cwd(), ".claude", "skills")
  : path.join(process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), ".claude"), "skills");
const dest = path.join(root, SKILL);

if (args.has("--uninstall")) {
  if (fs.existsSync(dest)) {
    fs.rmSync(dest, { recursive: true, force: true });
    console.log(green("✓") + ` Removed ${dest}`);
  } else {
    console.log(`Nothing to remove at ${dest}`);
  }
  process.exit(0);
}

// Keep a copy of a previous install the user may have edited.
if (fs.existsSync(dest)) {
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  const backup = path.join(os.tmpdir(), `${SKILL}-skill-backup-${stamp}`);
  fs.cpSync(dest, backup, { recursive: true });
  fs.rmSync(dest, { recursive: true, force: true });
  console.log(dim(`Previous version backed up to ${backup}`));
}

fs.mkdirSync(root, { recursive: true });
fs.cpSync(SRC, dest, { recursive: true });
console.log(green("✓") + ` Installed ${bold(SKILL)} skill ${pkg.version} → ${dest}`);

// Friendly dependency check (the skill itself also explains what's missing).
function has(cmd) {
  const r = spawnSync(process.platform === "win32" ? "where" : "which", [cmd], { stdio: "ignore" });
  return r.status === 0;
}
const chromeKnown = [
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
  ...[process.env.PROGRAMFILES, process.env["PROGRAMFILES(X86)"], process.env.LOCALAPPDATA]
    .filter(Boolean)
    .flatMap((b) => [
      path.join(b, "Google", "Chrome", "Application", "chrome.exe"),
      path.join(b, "Microsoft", "Edge", "Application", "msedge.exe"),
    ]),
];
const checks = [
  ["Python 3", has("python3") || has("python")],
  ["Chrome, Chromium or Edge", ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge"].some(has) || chromeKnown.some((p) => fs.existsSync(p))],
  ["Claude Code", has("claude")],
];
const missing = checks.filter(([, ok]) => !ok).map(([n]) => n);
if (missing.length) {
  console.log(yellow("!") + ` Not found on this machine: ${missing.join(", ")}. The skill needs these to render the PDF.`);
}

console.log(`
Next: open Claude Code in your project (or any folder) and say
  ${bold('"Make me a pitch deck for investors"')}   or type  ${bold("/pitch-deck")}

No code? That's fine. It will ask for your plan, your website, or a few questions.
Tip: for screenshots of logged-in pages, add the Playwright MCP:
  ${dim("claude mcp add playwright -- npx @playwright/mcp@latest")}`);
