"""Preflight figure PDFs: no Type 3 fonts, exact page width, palette greyscale spread.

python check_figs.py --width-in 3.25 fig1.pdf [fig2.pdf ...]   (width optional; tolerance 0.02in)
Exit code 1 on any FAIL; WARN (poppler render warnings, e.g. a CFF/OTF font
embedded under fonttype 42) prints but does not fail - switch to a TrueType font. Needs poppler-utils (pdffonts, pdfinfo).
"""
import argparse, re, subprocess, sys


def fonts(pdf):
    out = subprocess.run(["pdffonts", pdf], capture_output=True, text=True, check=True).stdout
    lines = out.splitlines()
    dash = lines[1].split(" ")  # column widths from the dashed header rule
    cuts, pos = [], 0
    for d in dash:
        cuts.append((pos, pos + len(d))); pos += len(d) + 1
    col = lambda r, i: r[cuts[i][0]:cuts[i][1]].strip()
    return [(col(r, 0), col(r, 1), col(r, 3)) for r in lines[2:] if r.strip()]


def width_in(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True, check=True).stdout
    m = re.search(r"Page size:\s+([\d.]+) x ([\d.]+) pts", out)
    return float(m.group(1)) / 72, float(m.group(2)) / 72


def render_warnings(pdf):
    """Render page 1 at low dpi with poppler; return its warnings (e.g. CFF font under a TrueType tag)."""
    r = subprocess.run(["pdftoppm", "-r", "20", "-f", "1", "-l", "1", "-png", pdf, "/tmp/_chkfig"],
                       capture_output=True, text=True)
    return sorted({l.strip() for l in r.stderr.splitlines() if l.strip()})


def luminance(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--width-in", type=float)
    ap.add_argument("pdfs", nargs="+")
    a = ap.parse_args()
    bad = 0
    for p in a.pdfs:
        f = fonts(p); w, h = width_in(p)
        t3 = [x for x in f if "Type 3" in x[1]]
        notemb = [x for x in f if x[2] != "yes"]
        ok_w = a.width_in is None or abs(w - a.width_in) <= 0.02
        warn = render_warnings(p)
        status = ("OK" if not warn else "WARN") if not t3 and not notemb and ok_w else "FAIL"
        bad += status == "FAIL"
        print(f"{status} {p}: {w:.3f}x{h:.3f}in fonts={[x[0].split('+')[-1] + ':' + x[1] for x in f]}"
              + (" TYPE3!" if t3 else "") + (" NOT-EMBEDDED!" if notemb else "")
              + ("" if ok_w else f" WIDTH!={a.width_in}") + (f" RENDER-WARN={warn}" if warn else ""))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
