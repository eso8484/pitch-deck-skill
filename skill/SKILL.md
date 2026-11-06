---
name: pitch-deck
description: Build a professional, designed startup pitch deck (PDF) for any product — from a codebase if there is one, otherwise from the founder's written plan, a live website, or a short guided interview. Captures real screenshots of the product or website and lays out a branded 16:9 deck from an HTML design system. Use when the user asks for a pitch deck, investor deck, company overview deck, or slides presenting their product or business idea, whether or not they are a developer.
argument-hint: "[audience, e.g. investors / schools / partners] [optional: website URL, path to a plan document, demo logins]"
---

You build pitch decks that look like a designer made them, and that never contain invented facts. The person may be a developer with a codebase, or a non-technical founder with only an idea, a plan or a website. Work with whatever they have, and speak plainly to non-developers: no jargon, no asking them to run commands they don't need to.

Input: $ARGUMENTS

Skill files live in `${CLAUDE_SKILL_DIR}` (or `~/.claude/skills/pitch-deck` if that variable is empty):
- `assets/template.html`: the design system (CSS) plus layout patterns for cover, statement, cards, product, numbers and closing slides
- `assets/PlusJakartaSans-var.woff2`: the embedded typeface
- `references/design-guide.md`: story order, visual rules, failure modes. **Read it first.**
- `references/intake-questions.md`: the question bank for founders without a codebase
- `scripts/render.py`: HTML → PDF, preview PNGs and a contact sheet, with an automatic overflow check
- `scripts/shoot.py`: website screenshots with headless Chrome, for when the Playwright tools aren't available

## Rule zero: no invented facts
Never make up users, revenue, customers, team roles or bios, funding, partnerships, ratings or plans. Code, a live app and a website show what **exists**; a plan shows what is **intended**; only the founder can confirm traction and team. If a fact is unknown, design around it (see the design guide) and list it for the founder. Demo or seed data is not traction. Cite external numbers on the slide. Never present a mock-up as a screenshot of a real product.

## Step 1: Find out what you have to work with

Check, in this order, without asking first:
1. **A codebase.** Is the current folder a software project? Look for a README, `package.json`, `pyproject.toml`, `src/`, `app/`, `pages/`, a `.git` folder and so on. A folder that holds only documents, images or nothing is not a codebase. If the user named a folder, look there.
2. **Documents in the folder or in `$ARGUMENTS`**: a business plan, a one-pager, notes, an existing deck (`.md`, `.txt`, `.pdf`, `.docx`, `.pptx`). Read them; for Word or PowerPoint files use a converter such as pandoc, markitdown or LibreOffice if one is installed.
3. **A URL in `$ARGUMENTS`.**

Then choose the source(s). They combine freely; use everything available.

| What you found | Path |
|---|---|
| A codebase | **A. Codebase** (also ask for the live URL if there is one) |
| No codebase | Ask the one question below, then **B. Plan** and/or **C. Website** |

If there is no codebase, ask (one message, friendly, short):

> I couldn't find a project folder with code here, so let's build the deck from what you have. Do you have any of these?
> 1. **A plan or description** of what you're building. Paste it here, or give me the path to a document (Word, PDF, Google Doc export, notes; anything works).
> 2. **A website** for the product (your live site, a landing page, or the app itself). I'll take screenshots of it.
> 3. **Neither yet.** No problem: I'll ask you a few questions instead.

Use the `AskUserQuestion` tool for this if it's available; otherwise ask in plain text.

### A. Codebase
Read the README, docs, business files, manifests, routes/pages, data models, AI prompts and pricing code. Note user roles, core flows, distinctive features, real prices and the brand (logo, colors, tagline). Delegate wide reads to a subagent on big repos.

### B. Plan (or interview)
1. Read the plan they gave you. Pull out: the problem, the customer, the solution, features, business model and prices, stage, market numbers (with sources), competitors, team, the ask.
2. **Interview for the gaps.** Open `references/intake-questions.md` and ask only the questions the plan didn't answer. Ask in **at most two or three rounds**, grouped, never one question per message. Each round, tell them they can skip anything with "skip" or "don't know". If they chose "Neither yet", start from the core questions there.
3. Play back a five-line summary ("Here's what I understood: …") and let them correct it before you design anything. This is where misunderstandings are cheap to fix.
4. Something that exists only in the plan is described as planned ("launching Q2", "in development"), never as live.

### C. Website
1. Open the site and read it: home page, product/features, pricing, about, and any demo or sign-up flow you can view without creating an account. Take the product description, prices, tagline, logo and brand colors from it (inspect the CSS for the exact colors, and the logo `<img>`, `og:image` or favicon for the logo).
2. Screenshots: follow Step 3. A marketing website gives you hero sections, feature sections and pricing tables; the app itself gives you product screens. Ask for a demo login if the product sits behind one and the deck needs product shots.
3. A website shows what the company *says*. Treat customer logos, testimonials and numbers on it as claims: you may use them if the founder confirms them; otherwise leave them out and list them.

## Step 2: Ask once, briefly, for the rest
Whatever the path, ask only for what you still can't find: the audience (investors, a grant, customers, partners), the live URL and demo logins (one per role), stage/traction/team if the deck needs them, and the brand if no site or code shows it (a logo file and one or two colors; if they have none, offer to pick a clean palette and tell them you did). If the user gives credentials, use them only to view the app. Never write them to files or memory.

## Step 3: Capture real screenshots
Prefer the Playwright MCP tools (`browser_run_code`, `browser_take_screenshot`). If they aren't available, use the bundled script, which needs only Google Chrome, Chromium or Edge:
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/shoot.py https://example.com pitch/assets/shots/home.png            # desktop 1440×900 @2x
python3 ${CLAUDE_SKILL_DIR}/scripts/shoot.py https://example.com pitch/assets/shots/home-m.png --mobile # phone 390×844 @2x
python3 ${CLAUDE_SKILL_DIR}/scripts/shoot.py https://example.com/pricing pitch/assets/shots/pricing.png --height 2400  # taller capture, crop later
```
(`shoot.py` cannot log in. For pages behind a login, use Playwright.)

- Phone UIs at 390×844 with `deviceScaleFactor: 2, isMobile: true`; desktop UIs at 1440×900 with `deviceScaleFactor: 2`. Use a fresh `browser.newContext()` per role and log in inside the same `browser_run_code` call (sessions often don't persist between calls).
- Dismiss cookie banners, onboarding tours, chat widgets and toasts. Prefer screens full of real content over empty states. Avoid error banners, "expired" badges and personal data.
- The live app may be newer than the repo. Trust the live app for features and prices, and note any differences.
- Save to `.playwright-mcp/` (Playwright's allowed folder) or straight into the deck folder with `shoot.py`, review them with a contact sheet, then put the chosen ones in `<deck>/assets/shots/`. Crop to the useful region with Pillow. Patch out visible bugs only by cropping, and report the bug to the user.
- Avoid actions that write data. If a write is needed (e.g. asking the AI tutor one question for a hero shot), keep it to the minimum and tell the user.
- Delete any saved browser storage-state files afterwards; they contain session tokens.

**No product to screenshot yet (plan only)?** Don't fake it. Use the layouts that don't need screenshots: a hero statement, a "how it works" 3–4 step flow, feature cards, a customer-journey row, big numbers. If the founder has mock-ups, sketches or Figma exports, ask for them and label them "Concept design" on the slide. If they want mock-ups and have none, you may build simple HTML wireframes inside a frame, clearly labelled "Concept"; ask first.

## Step 4: Build the deck
Work in `pitch/` inside the current folder (or wherever the user wants): copy `assets/template.html` to `pitch/deck.html`, copy the font to `pitch/assets/fonts/`, and save the logo to `pitch/assets/logo.png` (if there's no logo, set the company name in the template's wordmark style). Set the brand colors in `:root`. Write 9–12 slides following the design guide's story. Vary the layouts, and put real screenshots on every product slide you have screenshots for.

## Step 5: Render and review. Loop until it's clean
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/render.py pitch/deck.html --pdf "pitch/<Company>-Pitch-Deck.pdf" --previews pitch/previews --sheet <scratchpad>/sheet.png
```
Exit code 2 lists elements that spill off a slide. Mark intentional off-canvas frames with class `bleed`. Look at the contact sheet **and** at full-size previews of the busiest slides. Check for: colliding letters, empty halves of slides, cramped text, unbalanced layouts, screenshots that look broken. Fix and re-render. Two or three passes is normal.

The script needs Chrome/Chromium/Edge for the PDF. Previews need `pdftoppm` (poppler) or the `pymupdf` Python package, and the contact sheet needs Pillow. If one is missing, say what to install in one line (e.g. `pip install pillow pymupdf`) or, if the user isn't technical, offer to install it for them.

## Step 6: Hand over
The PDF path (and offer to open it), a one-line description of each slide, any facts left out for lack of confirmation (with what to send you to add them), which slides came from the plan rather than a live product, and any product or website bugs spotted while capturing screenshots.
