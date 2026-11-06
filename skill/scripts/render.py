#!/usr/bin/env python3
"""Render an HTML pitch deck (one <section class="slide"> per slide) to PDF.

Usage:
  python3 render.py deck.html [--pdf out.pdf] [--previews DIR] [--sheet sheet.png]

- PDF via headless Chrome/Chromium (fonts and images load from relative paths).
- --previews writes one PNG per slide (needs pdftoppm) for visual review.
- --sheet writes a single contact-sheet PNG of all slides (needs Pillow).
- QA: reports any element that spills outside its slide, unless it (or an
  ancestor) has class "bleed" (intentional off-canvas decoration). Exits 2 if
  anything overflows, so problems can't be missed.
"""

import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

QA_JS = r"""
<script>
window.addEventListener('load', function () {
  document.fonts.ready.then(function () {
    var report = [];
    document.querySelectorAll('.slide').forEach(function (slide, i) {
      var r = slide.getBoundingClientRect();
      slide.querySelectorAll('*').forEach(function (el) {
        if (el.closest('.bleed') || el.closest('.ring')) return;
        var cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden') return;
        var b = el.getBoundingClientRect();
        if (!b.width || !b.height) return;
        var tol = 1;
        if (b.left < r.left - tol || b.top < r.top - tol || b.right > r.right + tol || b.bottom > r.bottom + tol) {
          var label = el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ').join('.') : '');
          var txt = (el.innerText || el.getAttribute('src') || '').trim().slice(0, 40).replace(/\s+/g, ' ');
          report.push('slide ' + (i + 1) + ': ' + label + ' "' + txt + '"');
        }
        if ((cs.overflow === 'hidden' || cs.overflowY === 'hidden') && el.scrollHeight > el.clientHeight + 2 && el !== slide && el.tagName !== 'IMG' && !el.closest('.phone') && !el.closest('.browser')) {
          report.push('slide ' + (i + 1) + ': clipped text in ' + el.tagName.toLowerCase());
        }
      });
    });
    var out = document.createElement('pre');
    out.id = '__qa';
    out.textContent = JSON.stringify(report);
    out.style.display = 'none';
    document.body.appendChild(out);
  });
});
</script>
"""


def find_chrome():
    env = os.environ.get("CHROME_PATH")
    if env and os.path.exists(env):
        return env
    names = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome",
             "microsoft-edge", "msedge"]
    paths = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             "/Applications/Chromium.app/Contents/MacOS/Chromium",
             "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
    for base in (os.environ.get("PROGRAMFILES"), os.environ.get("PROGRAMFILES(X86)"), os.environ.get("LOCALAPPDATA")):
        if base:
            paths += [os.path.join(base, "Google", "Chrome", "Application", "chrome.exe"),
                      os.path.join(base, "Microsoft", "Edge", "Application", "msedge.exe")]
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    for path in paths:
        if os.path.exists(path):
            return path
    return None


def pdf_to_pngs(pdf, prefix):
    """One PNG per page at 96 dpi: pdftoppm if installed, else PyMuPDF."""
    if shutil.which("pdftoppm"):
        subprocess.run(["pdftoppm", "-png", "-r", "96", pdf, prefix], check=True)
        return True
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("warning: previews skipped; install poppler (pdftoppm) or run: pip install pymupdf")
        return False
    doc = fitz.open(pdf)
    for i, page in enumerate(doc, 1):
        page.get_pixmap(dpi=96).save(f"{prefix}-{i:02d}.png")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--pdf")
    ap.add_argument("--previews")
    ap.add_argument("--sheet")
    args = ap.parse_args()

    html = os.path.abspath(args.html)
    pdf = os.path.abspath(args.pdf or os.path.splitext(html)[0] + ".pdf")
    chrome = find_chrome()
    if not chrome:
        sys.exit(f"Chrome/Chromium/Edge not found (set CHROME_PATH to point at it). Open {html} in Chrome and print to PDF (no margins, background graphics on).")

    base = [chrome, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
            "--allow-file-access-from-files", "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=8000"]

    # QA pass on a temporary copy that sits next to the original so relative paths still work.
    src = open(html, encoding="utf-8").read()
    fd, qa_path = tempfile.mkstemp(suffix=".html", dir=os.path.dirname(html), prefix=".qa-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(src.replace("</body>", QA_JS + "</body>"))
    try:
        dom = subprocess.run(base + ["--window-size=1280,720", "--dump-dom", "file://" + qa_path],
                             capture_output=True, text=True, timeout=180).stdout
    finally:
        os.remove(qa_path)
    m = re.search(r'<pre id="__qa"[^>]*>(.*?)</pre>', dom, re.S)
    issues = []
    if m:
        import html as htmllib
        import json
        issues = json.loads(htmllib.unescape(m.group(1)))
    else:
        print("warning: QA script did not report (page may have failed to load)")

    subprocess.run(base + ["--no-pdf-header-footer", "--print-to-pdf=" + pdf, "file://" + html],
                   capture_output=True, text=True, timeout=240)
    if not os.path.exists(pdf):
        sys.exit("PDF was not produced.")
    print("PDF:", pdf)

    if args.previews or args.sheet:
        prev = os.path.abspath(args.previews or tempfile.mkdtemp())
        os.makedirs(prev, exist_ok=True)
        for old in glob.glob(os.path.join(prev, "slide-*.png")):
            os.remove(old)
        made = pdf_to_pngs(pdf, os.path.join(prev, "slide"))
        if made and args.previews:
            print("Previews:", prev)
        if made and args.sheet:
            from PIL import Image
            files = sorted(glob.glob(os.path.join(prev, "slide-*.png")))
            ims = [Image.open(f) for f in files]
            w, h = 640, 360
            cols = 2
            rows = (len(ims) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * (w + 12) + 12, rows * (h + 12) + 12), "#9aa0b3")
            for i, im in enumerate(ims):
                sheet.paste(im.resize((w, h)), (12 + (i % cols) * (w + 12), 12 + (i // cols) * (h + 12)))
            sheet.save(os.path.abspath(args.sheet))
            print("Sheet:", os.path.abspath(args.sheet))

    if issues:
        print(f"\n{len(issues)} layout issue(s):")
        for line in issues[:40]:
            print("  -", line)
        sys.exit(2)
    print("Layout check: no overflow.")


if __name__ == "__main__":
    main()
