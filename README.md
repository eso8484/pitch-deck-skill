# pitch-deck-skill

A [Claude Code](https://claude.com/claude-code) skill that builds a professional, designed 16:9 pitch deck as a PDF, for developers and non-developers alike.

- **Have a codebase?** It reads the code and screenshots your running app.
- **Have a plan?** Paste it or point to a document (Word, PDF, notes). It interviews you for the gaps.
- **Have a website?** It reads the site and takes screenshots of it.
- **Have only an idea?** It asks you a short set of questions.

It never invents traction, customers, team or numbers. Anything it can't confirm is listed for you instead of being put on a slide.

## Install

```bash
npx pitch-deck-skill
```

This copies the skill to `~/.claude/skills/pitch-deck`, so it works in every folder. To install into the current folder only:

```bash
npx pitch-deck-skill --project
```

Then open Claude Code and say *"Make me a pitch deck for investors"*, or type `/pitch-deck`.

## Requirements

- Claude Code
- Python 3
- Google Chrome, Chromium or Microsoft Edge (for the PDF and screenshots)
- Optional: `pip install pillow pymupdf` for slide previews and the contact sheet; the Playwright MCP for screenshots of pages behind a login (`claude mcp add playwright -- npx @playwright/mcp@latest`)

## Update / remove

```bash
npx pitch-deck-skill@latest          # update (your old copy is backed up to the temp folder)
npx pitch-deck-skill --uninstall
```
