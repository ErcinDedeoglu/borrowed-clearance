#!/usr/bin/env python3
"""Write v32b/MANIFEST.json for the current paper version (v3.2b): v31/MANIFEST.json with
- the three diagrams redrawn at 6.5in by widen_v32.py (fig_threat, fig_traj_schematic, fig_design_v31) pointing to v32/,
- the related-evaluations table (v32b/tab_positioning.tex) and its evidence file (v32b/positioning_v32b.json,
  shipped with the arXiv source as anc/positioning_v32b.json) written by make_positioning_v32b.py, added as input J
  (as in the paper's provenance table; its sources v31/positioning_v31.json, when present, and v32b/tab_positioning_notes.tex are hashed
  with the scripts; this release does not include v31/positioning_v31.json, so it is not listed).
Run from paper/figs after widen_v32.py, strip_meta.py v32/*.pdf and make_positioning_v32b.py:   python3 make_manifest_v32b.py"""
import json, hashlib, os
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(os.path.dirname(H))
sha = lambda p: hashlib.sha256(open(os.path.join(R, p), "rb").read()).hexdigest()
m = json.load(open(os.path.join(H, "v31", "MANIFEST.json")))
W = ("fig_threat.pdf", "fig_traj_schematic.pdf", "fig_design_v31.pdf")
for a in m["artifacts"]:
    b = os.path.basename(a["file"])
    if b in W:
        a["file"] = "paper/figs/v32/" + b; a["scripts"] += ", widen_v32.py"; a["sha256"] = sha(a["file"])
m["artifacts"].append({"file": "paper/figs/v32b/tab_positioning.tex", "inputs": "J", "object": "Table related evaluations",
                       "scripts": "make_positioning_v32b.py", "sha256": sha("paper/figs/v32b/tab_positioning.tex")})
m["outputs"] = {k: v for k, v in m["outputs"].items() if os.path.basename(k) not in W}
for a in m["artifacts"]:
    if a["file"].startswith(("paper/figs/v32/", "paper/figs/v32b/")): m["outputs"][a["file"]] = a["sha256"]
m["outputs"]["paper/figs/v32b/positioning_v32b.json"] = sha("paper/figs/v32b/positioning_v32b.json")
m["outputs"] = dict(sorted(m["outputs"].items()))
m["inputs"]["J"] = {"paper/figs/v32b/positioning_v32b.json": sha("paper/figs/v32b/positioning_v32b.json")}
for s in ["paper/figs/v31/positioning_v31.json", "paper/figs/v32b/tab_positioning_notes.tex", "paper/figs/widen_v32.py", "paper/figs/make_positioning_v32b.py", "paper/figs/make_manifest_v32b.py",
          "paper/figs/tikz/v32/fig_design_v31.tex", "paper/figs/tikz/v32/fig_threat.tex", "paper/figs/tikz/v32/fig_traj_schematic.tex"]:
    if os.path.exists(os.path.join(R, s)): m["scripts"][s] = sha(s)
m["scripts"] = dict(sorted(m["scripts"].items()))
m["note"] += ("; v3.2: fig_threat, fig_traj_schematic and fig_design_v31 redrawn at 6.5in by widen_v32.py from tikz/v31 "
              "(horizontal spacing only); v3.2a: This work P5 partial; v3.2b: tab_positioning.tex and positioning_v32b.json written by make_positioning_v32b.py (retrieval note dated)")
json.dump(m, open(os.path.join(H, "v32b", "MANIFEST.json"), "w"), indent=1, sort_keys=True)
print("wrote v32b/MANIFEST.json")
