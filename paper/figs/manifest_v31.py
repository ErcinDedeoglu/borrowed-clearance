"""Write figs/v31/MANIFEST.json (sha256 of every v3.1 exhibit, the script that wrote it and its inputs) and
figs/v31/tab_provenance.tex (the reproducibility table, generated from MANIFEST.json; it is not listed in itself).
Run from paper/figs after make_exhibits_v31.py, make_figs_v31.py, redraw_v31.py, make_tabs_v31.py and strip_meta.py."""
import glob, hashlib, json, os, platform
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, "..", ".."))
O = os.path.join(H, "v31")
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
rel = lambda p: os.path.relpath(p, ROOT)
MODELS = ("Qwen2.5-0.5B-Instruct", "Qwen2.5-1.5B-Instruct", "SmolLM2-1.7B-Instruct", "Qwen2.5-3B-Instruct")
EP = [os.path.join(ROOT, "runs/main", m, "episodes.jsonl") for m in MODELS]
PIL = [os.path.join(ROOT, "runs/pilot/episodes.jsonl"), os.path.join(ROOT, "runs/pilot-v02/episodes.jsonl")]
HARN = [os.path.join(ROOT, "code/bcharness", f) for f in ("scenarios.py", "agent.py", "bank.py", "verifier.py", "crypto.py", "policies.py")]
ST = os.path.join(O, "stats_v3.json"); EX = os.path.join(O, "exhibits_v3.json"); PO = os.path.join(O, "positioning_v31.json")
REP = os.path.join(ROOT, "runs/main/analysis/factorial-report.md")
# input groups (keys used in the table)
PRE = os.path.join(ROOT, "prereg-2026-10-30.md")  # frozen pre-registration
G = {"D": [PRE], "E": EP, "P": PIL, "H": HARN, "S": [ST], "X": [EX], "J": [PO], "R": [REP]}
if not os.path.exists(PO): del G["J"]  # related-work comparison record: not part of the public release
# stats_v3.json is made by stats_v3.py from E; exhibits_v3.json by make_exhibits_v31.py from E and H
s = lambda f: os.path.join(H, f)
ART = [  # (paper object, output file in v31/, script, input keys)
 ("Fig. threat model", "fig_threat.pdf", "make_exhibits_v31.py, make_figs_v31.py", "H"),
 ("Fig. harness", "fig_harness_v31.pdf", "make_figs_v31.py (tikz/v31/fig_harness_v31.tex)", "H"),
 ("Fig. trajectory schematic", "fig_traj_schematic.pdf", "make_exhibits_v31.py, make_figs_v31.py", "E, H, X"),
 ("Table main results", "tab_main.tex", "make_figs.py, make_tabs_v31.py", "E"),
 ("Fig. execution by arm", "fig_main_arm.pdf", "redraw_v31.py", "E"),
 ("Fig. option order", "fig_dumbbell.pdf", "make_figs_v31.py", "S"),
 ("Fig. channel-variant heatmap", "fig_heat.pdf", "make_figs_v31.py", "S"),
 ("Fig. trajectory decomposition", "fig_flow.pdf", "make_figs_v31.py", "S"),
 ("Fig. verify-then-ignore by reason", "fig_vti.pdf", "make_figs_v31.py", "S"),
 ("Table failure modes", "tab_taxonomy.tex", "make_tabs_v31.py", "S"),
 ("Fig. safety against utility", "fig_frontier.pdf", "make_figs_v31.py", "S"),
 ("Table related evaluations", "tab_positioning.tex", "make_tabs_v31.py", "J"),
 ("Fig. pilot", "fig_pilot.pdf", "redraw_v31.py", "P"),
 ("Table pilot", "tab_pilot.tex", "make_figs.py, make_tabs_v31.py", "P"),
 ("Fig. design", "fig_design_v31.pdf", "make_figs_v31.py (tikz/v31/fig_design_v31.tex)", "D"),
 ("Fig. execution by condition", "fig_main_wording.pdf", "redraw_v31.py", "E"),
 ("Fig. execution by variant", "fig_main_variant.pdf", "redraw_v31.py", "E"),
 ("Table per-condition rates", "tab_percond.tex", "make_tab_percond.py, make_tabs_v31.py", "R"),
 ("Table paired tests", "tab_tests.tex", "make_tabs_v31.py", "S"),
 ("Table channel marginals", "tab_channel.tex", "make_tabs_v31.py", "S"),
 ("Table run manifests", "tab_repro.tex", "make_tabs_v31.py", "S"),
 ("Table failure-mode examples", "tab_taxexamples.tex", "make_tabs_v31.py", "S"),
 ("Fig. verbatim trajectories", "fig_traj_full.pdf", "make_exhibits_v31.py, make_figs_v31.py", "E, H, X"),
 ("Prompts", "app_prompts.tex", "make_exhibits_v31.py", "H"),
 ("Table clearance strings", "tab_clearances.tex", "make_exhibits_v31.py", "H"),
 ("Trajectory gallery", "app_gallery.tex", "make_exhibits_v31.py", "E, H, X"),
]
ART = [x for x in ART if x[3] != "J" or os.path.exists(PO)]  # tab_positioning.tex needs the comparison record
scripts = [s(f) for f in ("make_exhibits_v3.py", "make_exhibits_v31.py", "make_figs.py", "make_figs_v31.py", "redraw_v31.py", "stats_v3.py",
                          "make_tabs_v31.py", "make_tab_percond.py", "v3_integrity.py", "manifest_v31.py")] + sorted(glob.glob(os.path.join(H, "tikz", "v31", "*.tex")))
outs = sorted(set(glob.glob(os.path.join(O, "fig_*.pdf")) + glob.glob(os.path.join(O, "fig_*.svg")) + glob.glob(os.path.join(O, "fig_*.csv")) +
                  glob.glob(os.path.join(O, "tab_*.tex")) + glob.glob(os.path.join(O, "app_*.tex")) + [os.path.join(O, "fig_traj_body.tex")]) - {os.path.join(O, "tab_provenance.tex")})
for _, f, _, _ in ART: assert os.path.exists(os.path.join(O, f)), f
m = {"python": platform.python_version(), "scripts": {rel(p): sha(p) for p in scripts},
     "inputs": {k: {rel(p): sha(p) for p in v} for k, v in G.items()},
     "outputs": {rel(p): sha(p) for p in outs},
     "artifacts": [{"object": a, "file": rel(os.path.join(O, f)), "scripts": sc, "inputs": i, "sha256": sha(os.path.join(O, f))} for a, f, sc, i in ART],
     "note": "PDF metadata stripped with strip_meta.py; widths checked with check_figs.py (6.5in = measured \\linewidth 469.755pt); "
             "stats_v3.json is made by stats_v3.py from E, exhibits_v3.json by make_exhibits_v31.py from E and H; tab_provenance.tex is generated from this file"}
json.dump(m, open(os.path.join(O, "MANIFEST.json"), "w"), indent=1, sort_keys=True)
e = lambda t: t.replace("_", r"\_")
tt = lambda t: r"\texttt{" + e(t) + "}"
L = [r"\begin{tabular}{@{}l>{\raggedright\arraybackslash}p{0.27\textwidth}>{\raggedright\arraybackslash}p{0.27\textwidth}ll@{}}\toprule",
     r"object & file in \texttt{figs/v31/} & script(s) in \texttt{figs/} & inputs & SHA-256 (first 12) \\ \midrule"]
for a in m["artifacts"]:
    L.append(f"{a['object']} & {tt(os.path.basename(a['file']))} & {e(a['scripts']).replace('/', '/' + chr(92) + 'allowbreak{}')} & {a['inputs']} & " + r"\texttt{" + a["sha256"][:12] + r"} \\")
L.append(r"\bottomrule\end{tabular}")
K = {"D": "pre-registration document, frozen 30 October 2026", "E": "main-run episode logs \\texttt{runs/main/*/episodes.jsonl} (hashes in Table~\\ref{tab:repro})",
     "P": "pilot episode logs \\texttt{runs/pilot*/episodes.jsonl}", "H": "harness sources \\texttt{code/bcharness/}",
     "S": "\\texttt{stats\\_v3.json} (made by \\texttt{stats\\_v3.py} from E)", "X": "\\texttt{exhibits\\_v3.json} (made by \\texttt{make\\_exhibits\\_v31.py} from E and H)",
     "J": "\\texttt{positioning\\_v31.json} (per-cell evidence from the cited papers)", "R": "pre-registered analysis report made by \\texttt{factorial.py} from E"}
def short(k):
    v = m["inputs"][k]
    return (" " + r"\texttt{" + list(v.values())[0][:12] + "}") if len(v) == 1 else ""
key = "; ".join(f"{k}: {K[k]}{short(k)}" for k in G)
open(os.path.join(O, "tab_provenance.tex"), "w").write("% generated by manifest_v31.py from MANIFEST.json -- do not edit\n"
    r"\footnotesize\setlength{\tabcolsep}{3pt}" + "\n\\fitbox{" + "\n".join(L) + "}\n\n\\smallskip{\\footnotesize Inputs. " + key + ".}\n")
print("MANIFEST", sum(len(v) for v in m["inputs"].values()), "inputs", len(m["outputs"]), "outputs", len(ART), "artifacts")
