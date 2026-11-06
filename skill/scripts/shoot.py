#!/usr/bin/env python3
"""Screenshot a web page with headless Chrome/Chromium/Edge (no Playwright needed).

Usage:
  python3 shoot.py URL OUT.png [--mobile] [--width W] [--height H] [--scale S] [--wait MS]

Defaults: desktop 1440x900 at 2x. --mobile uses 390x844 at 2x with a phone user agent.
--height lets you capture a taller strip of the page to crop later with Pillow.
Cannot log in; use the Playwright tools for pages behind a login.
"""

import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import find_chrome  # noqa: E402

MOBILE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
             "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("out")
    ap.add_argument("--mobile", action="store_true")
    ap.add_argument("--width", type=int)
    ap.add_argument("--height", type=int)
    ap.add_argument("--scale", type=float, default=2)
    ap.add_argument("--wait", type=int, default=6000, help="virtual time budget in ms for the page to settle")
    a = ap.parse_args()

    chrome = find_chrome()
    if not chrome:
        sys.exit("Chrome/Chromium/Edge not found. Install Google Chrome, or use the Playwright tools.")
    w = a.width or (390 if a.mobile else 1440)
    h = a.height or (844 if a.mobile else 900)
    out = os.path.abspath(a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cmd = [chrome, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
           f"--window-size={w},{h}", f"--force-device-scale-factor={a.scale}",
           f"--virtual-time-budget={a.wait}", f"--screenshot={out}"]
    if a.mobile:
        cmd.append(f"--user-agent={MOBILE_UA}")
    cmd.append(a.url)
    subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not os.path.exists(out):
        sys.exit("Screenshot was not produced (the page may have failed to load).")
    print("Saved:", out)


if __name__ == "__main__":
    main()
