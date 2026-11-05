"""v3.1 figures for the Borrowed Clearance paper, drawn only from v31/stats_v3.json (made by stats_v3.py from
runs/main/), v31/exhibits_v3.json and the TikZ sources in tikz/ and tikz/v31/. No number is typed here.
Run from paper/figs (paper/figs/requirements-figs-v3.txt; tectonic on PATH or $TECTONIC):   python make_figs_v31.py
Palette: Okabe-Ito (colour-blind safe) with redundant hatches/markers/line styles; heatmap uses cividis.
Figures are drawn at their final printed size (6.5in text width, frontier 4.5in) and included unscaled.
Writes v31/fig_threat.pdf, v31/fig_traj_schematic.pdf, v31/fig_traj_full.pdf, v31/fig_harness_v31.pdf, v31/fig_design_v31.pdf,
v31/fig_flow.pdf, v31/fig_heat.pdf, v31/fig_vti.pdf, v31/fig_dumbbell.pdf, v31/fig_frontier.pdf and a CSV per plotted figure."""
import csv, json, os, subprocess
import numpy as np
import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "v31")
TECTONIC = os.environ.get("TECTONIC", "tectonic")
S = json.load(open(os.path.join(OUT, "stats_v3.json")))
MODELS = ("Qwen2.5-0.5B-Instruct", "Qwen2.5-1.5B-Instruct", "SmolLM2-1.7B-Instruct", "Qwen2.5-3B-Instruct")
SHORT = {"Qwen2.5-0.5B-Instruct": "Qwen2.5-0.5B", "Qwen2.5-1.5B-Instruct": "Qwen2.5-1.5B",
         "SmolLM2-1.7B-Instruct": "SmolLM2-1.7B", "Qwen2.5-3B-Instruct": "Qwen2.5-3B (bf16)"}
ARMS = ("A0_none", "A1_prompt_rule", "A2_code_verifier", "A3_structured_status")
ALAB = {"A0_none": "A0 none", "A1_prompt_rule": "A1 prompt rule", "A2_code_verifier": "A2 code gate*",
        "A3_structured_status": "A3 structured status"}
ACOL = {"A0_none": "#000000", "A1_prompt_rule": "#0072B2", "A2_code_verifier": "#009E73", "A3_structured_status": "#D55E00"}
AHATCH = {"A0_none": None, "A1_prompt_rule": "....", "A2_code_verifier": "xxxx", "A3_structured_status": "////"}
JIT = {"A0_none": -1.5, "A1_prompt_rule": -0.5, "A2_code_verifier": 0.5, "A3_structured_status": 1.5}  # display offset only (pp)
AMK = {"A0_none": "o", "A1_prompt_rule": "s", "A2_code_verifier": "D", "A3_structured_status": "^"}
ALS = {"A0_none": "-", "A1_prompt_rule": "--", "A2_code_verifier": "-.", "A3_structured_status": ":"}
WIDTH = 6.5
PATTERNS = ("trust_by_position", "approvals_that_float", "content_as_authority")
PLAB = {"trust_by_position": "trust by position", "approvals_that_float": "approvals that float",
        "content_as_authority": "content as authority"}
VARIANTS = ("none", "peer_text_claim", "doc_embedded", "floating_approval", "signed_wrong_payload",
            "signed_expired", "replayed", "unentitled_signer", "valid")
VLABEL = {"none": "none", "peer_text_claim": "peer text", "doc_embedded": "doc text", "floating_approval": "floating",
          "signed_wrong_payload": "wrong payload", "signed_expired": "expired", "replayed": "replayed",
          "unentitled_signer": "unentitled", "valid": "valid"}
REASONS = ("no_clearance", "not_payload_bound", "payload_mismatch", "expired", "replayed", "signer_not_entitled")
FLOW = ("first_turn_execute", "verify_then_execute", "verify_then_halt", "first_turn_halt", "verify_loop", "unparsed")
FLAB = {"first_turn_execute": "execute on first turn", "verify_then_execute": "verify, INVALID, execute",
        "verify_then_halt": "verify, then halt", "first_turn_halt": "halt on first turn",
        "verify_loop": "verify loop, no action", "unparsed": "unparsed output"}
FCOL = {"first_turn_execute": "#D55E00", "verify_then_execute": "#E69F00", "verify_then_halt": "#56B4E9",
        "first_turn_halt": "#0072B2", "verify_loop": "#bdbdbd", "unparsed": "#636363"}
plt.rcParams.update({"font.family": "serif", "font.serif": ["Liberation Serif", "DejaVu Serif"], "mathtext.fontset": "stix", "svg.fonttype": "none", "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
                     "legend.fontsize": 7, "xtick.labelsize": 7, "ytick.labelsize": 7, "pdf.fonttype": 42,
                     "axes.spines.top": False, "axes.spines.right": False, "savefig.bbox": None, "figure.constrained_layout.use": True,
                     "svg.hashsalt": "bc", "pdf.compression": 6})
META = {"Creator": None, "Producer": None, "CreationDate": None}


def save(fig, name, rows):
    fig.savefig(os.path.join(OUT, name + ".pdf"), metadata=META)
    fig.savefig(os.path.join(OUT, name + ".svg"), metadata={"Creator": None, "Date": None}); plt.close(fig)
    if rows:
        with open(os.path.join(OUT, name + ".csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("wrote", name)


def traj_schematic():
    """v3.1 (M1): four-lane schematic of the same payment under each arm, built from the replayed tool sequence
    recorded in exhibits_v3.json (no raw text; the verbatim transcripts are in the appendix)."""
    X = json.load(open(os.path.join(OUT, "exhibits_v3.json")))["trajectory"]
    pat, var, d = X["cell"]
    assert var in ("peer_text_claim", "doc_embedded")        # unsigned claim -> verifier reason no_clearance
    inp = {"A0_none": "A0 input", "A1_prompt_rule": "A0 input + rule", "A2_code_verifier": "A0 input (gate in code)",
           "A3_structured_status": r"A0 input + status line\\{\ttfamily INVALID (no\_clearance)}"}
    fin = {"executed": ("ledger: EXECUTED", "oiVerm"), "halted": ("HALTED", "oiGreen!70!black"), "blocked": ("gate: BLOCKED", "oiBlue")}
    L = [r"% generated by make_figs_v31.py from v31/exhibits_v3.json -- do not edit",
         r"\documentclass[border=3pt]{standalone}\usepackage[T1]{fontenc}\usepackage{lmodern,tikz}\usetikzlibrary{arrows.meta,positioning}",
         r"\definecolor{oiBlue}{HTML}{0072B2}\definecolor{oiVerm}{HTML}{D55E00}\definecolor{oiGreen}{HTML}{009E73}\definecolor{oiOrange}{HTML}{E69F00}",
         r"\begin{document}\sffamily\begin{tikzpicture}[font=\footnotesize, b/.style={draw,rounded corners=2pt,inner sep=2.5pt,minimum height=6mm,align=center},"
         r" t/.style={b,font=\scriptsize\ttfamily,fill=gray!8}, r/.style={b,draw=none,font=\scriptsize\ttfamily,inner sep=1pt}, ar/.style={-{Latex[length=1.6mm]},thick}]"]
    for i, a in enumerate(ARMS):
        y = -1.25 * i; e = X[a]
        tools = [json.loads(t)["tool"] for t in e["steps"]]
        L.append(rf"\node[anchor=west,font=\footnotesize\bfseries,text width=2.3cm] (l{i}) at (0,{y}) {{{ALAB[a].replace('*', '')}}};")
        L.append(rf"\node[b,fill=oiOrange!10,text width=2.6cm,right=0.1cm of l{i}] (i{i}) {{{inp[a]}}};")
        prev = f"i{i}"
        for k, tl in enumerate(tools):
            L.append(rf"\node[t,right=0.35cm of {prev}] (s{i}{k}) {{{tl.replace('_', chr(92) + '_')}}};")
            L.append(rf"\draw[ar] ({prev}) -- (s{i}{k});"); prev = f"s{i}{k}"
            if tl == "verify_clearance":
                L.append(rf"\node[r,right=0.25cm of {prev}] (v{i}{k}) {{INVALID}};"); L.append(rf"\draw[ar,gray] ({prev}) -- (v{i}{k});"); prev = f"v{i}{k}"
        txt, col = fin[e["final"]]
        L.append(rf"\node[b,draw={col},text={col},font=\footnotesize\bfseries,line width=0.9pt,anchor=west] (f{i}) at (12.1,{y}) {{{txt}}};")
        L.append(rf"\draw[ar,{col}] ({prev}) -- (f{i});")
    L.append(r"\end{tikzpicture}\end{document}")
    open(os.path.join(TIKZ, "fig_traj_schematic.tex"), "w").write("\n".join(L) + "\n")


TIKZ = os.path.join(HERE, "tikz", "v31")


def traj_full():
    # verbatim 2x2 trajectories (appendix): standalone wrapper around v31/fig_traj_body.tex from make_exhibits_v31.py
    W = open(os.path.join(HERE, "tikz", "fig_traj.tex")).read().replace("make_exhibits_v3.py", "make_figs_v31.py").replace("../v3/fig_traj_body.tex", "../../v31/fig_traj_body.tex")
    assert "../../v31/fig_traj_body.tex" in W
    open(os.path.join(TIKZ, "fig_traj_full.tex"), "w").write(W)


def tikz():
    traj_schematic(); traj_full()
    for name in ("fig_threat", "fig_traj_schematic", "fig_traj_full", "fig_harness_v31", "fig_design_v31"):
        subprocess.run([TECTONIC, "-X", "compile", "--outdir", OUT, name + ".tex"], cwd=TIKZ, check=True, capture_output=True)
        print("wrote", name)


def flow():
    fig, axes = plt.subplots(1, 4, figsize=(WIDTH, 2.75), sharey=True)
    rows = []
    for ax, m in zip(axes, MODELS):
        y = np.arange(len(ARMS))[::-1]
        for yi, a in zip(y, ARMS):
            v = S["flow"][f"{m}|{a}"]; left = 0
            for f in FLOW:
                hat = "////" if (a == "A2_code_verifier" and f in ("first_turn_execute", "verify_then_execute")) else None
                ax.barh(yi, v[f], left=left, color=FCOL[f], height=0.7, edgecolor="white", lw=0.3, hatch=hat,
                        label=FLAB[f] if (m == MODELS[0] and a == ARMS[0]) else None)
                if v[f] >= 30:
                    ax.text(left + v[f] / 2, yi, str(v[f]), ha="center", va="center", fontsize=5.5,
                            color="white" if (f in ("first_turn_execute", "first_turn_halt", "unparsed") and not hat) else "black",
                            bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none") if hat else None)
                left += v[f]
                rows.append({"model": m, "arm": a, "category": f, "count": v[f]})
            if a == "A2_code_verifier":
                blk = S["flow_blocked"][f"{m}|{a}"]
                assert blk == v["first_turn_execute"] + v["verify_then_execute"], (m, blk)
                rows.append({"model": m, "arm": a, "category": "blocked_by_gate", "count": blk})
        ax.set_yticks(y); ax.set_yticklabels([ALAB[a] for a in ARMS]); ax.set_xlim(0, 384)
        ax.set_xticks([0, 128, 256, 384]); ax.set_title(SHORT[m])
    fig.supxlabel("non-valid episodes per arm (n=384)", fontsize=8)
    from matplotlib.patches import Patch
    h, l = axes[0].get_legend_handles_labels()
    h.append(Patch(facecolor="#dddddd", hatch="////", edgecolor="white", label="A2 (hatched): attempted execute, blocked by the gate")); l.append(h[-1].get_label())
    fig.legend(h, l, loc="outside lower center", ncol=3, frameon=False)
    save(fig, "fig_flow", rows)


def heat():
    arms = ("A0_none", "A1_prompt_rule", "A3_structured_status")
    cmap = plt.get_cmap("cividis")
    fig, axes = plt.subplots(4, 3, figsize=(WIDTH, 5.0), sharex=True, sharey=True)
    rows = []
    for i, m in enumerate(MODELS):
        for j, a in enumerate(arms):
            ax = axes[i, j]; h = S["heat"][f"{m}|{a}"]
            M = np.array([[h[f"{p}|{v}"] for v in VARIANTS] for p in PATTERNS])
            im = ax.imshow(M, cmap=cmap, vmin=0, vmax=16, aspect="auto")
            for pi in range(3):
                for vi in range(9):
                    rgb = cmap(M[pi, vi] / 16)[:3]; lum = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
                    ax.text(vi, pi, str(M[pi, vi]), ha="center", va="center", fontsize=5.5, fontweight="bold",
                            color="black" if lum > 0.45 else "white")
                    rows.append({"model": m, "arm": a, "pattern": PATTERNS[pi], "variant": VARIANTS[vi], "executed": int(M[pi, vi]), "n": 16})
            ax.axvline(7.5, color="white", lw=1.6)
            ax.set_yticks(range(3)); ax.set_yticklabels([PLAB[p].replace(" ", "\n", 1) if p != "content_as_authority" else "content as\nauthority" for p in PATTERNS], fontsize=6)
            ax.set_xticks(range(9)); ax.set_xticklabels([VLABEL[v] for v in VARIANTS], rotation=45, ha="right", fontsize=6, rotation_mode="anchor")
            for s in ax.spines.values(): s.set_visible(False)
            if i == 0: ax.set_title(ALAB[a])
            if j == 0: ax.set_ylabel(SHORT[m], fontweight="bold", fontsize=7)
    cb = fig.colorbar(im, ax=axes, fraction=0.02, pad=0.01); cb.set_label("executed out of 16")
    save(fig, "fig_heat", rows)


def vti():
    ms = ("Qwen2.5-0.5B-Instruct", "SmolLM2-1.7B-Instruct")
    arms = ("A0_none", "A1_prompt_rule", "A3_structured_status")
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 2.6), sharey=True)
    rows = []; x = np.arange(len(REASONS)); w = 0.26
    for ax, m in zip(axes, ms):
        for j, a in enumerate(arms):
            d = [S["vti_reason"][f"{m}|{a}"][r] for r in REASONS]
            p = np.array([v["pct"] if v["n"] else np.nan for v in d]); lo = np.array([v["lo"] if v["n"] else np.nan for v in d])
            hi = np.array([v["hi"] if v["n"] else np.nan for v in d])
            xs = x + (j - 1) * w
            ax.bar(xs, p, w * 0.92, color=ACOL[a], label=ALAB[a], zorder=2, hatch=AHATCH[a], edgecolor="white", lw=0.3)
            ax.errorbar(xs, p, yerr=[p - lo, hi - p], fmt="none", ecolor="black", elinewidth=0.6, capsize=1.2, zorder=3)
            for xi, v in zip(xs, d):
                if v["n"]:
                    ax.text(xi, min(v["hi"], 100) + 2, str(v["n"]), ha="center", va="bottom", fontsize=4.8, rotation=90)
                else:
                    ax.text(xi, 2, "n=0", ha="center", va="bottom", fontsize=4.8, rotation=90, color="gray")
            for r, v in zip(REASONS, d):
                rows.append({"model": m, "arm": a, "reason": r, **{k: v[k] for k in ("k", "n", "pct", "lo", "hi")}})
        ax.set_xticks(x); ax.set_xticklabels([r.replace("_", " ") for r in REASONS], rotation=25, ha="right")
        ax.set_ylim(0, 118); ax.set_yticks([0, 25, 50, 75, 100]); ax.grid(axis="y", lw=0.3, zorder=0); ax.set_title(SHORT[m])
    axes[0].set_ylabel("executed after own INVALID (%)\n(number above bar: n episodes)")
    fig.legend(*axes[0].get_legend_handles_labels(), loc="outside upper center", frameon=False, ncol=3)
    for m in ("Qwen2.5-1.5B-Instruct", "Qwen2.5-3B-Instruct"):
        for a in ARMS:
            d = S["vti_reason"][f"{m}|{a}"]["all"]; rows.append({"model": m, "arm": a, "reason": "all", **{k: d[k] for k in ("k", "n", "pct", "lo", "hi")}})
    save(fig, "fig_vti", rows)


def dumbbell():
    arms = ("A0_none", "A1_prompt_rule", "A3_structured_status")
    ws = ("W1_list", "W2_question", "W3_options")
    fig, axes = plt.subplots(1, 4, figsize=(WIDTH, 3.3), sharey=True, sharex=True)
    rows = []
    labels = [f"{w.split('_')[0]} {ALAB[a].split(' ')[0]}" for w in ws for a in arms] + [f"{w} {ALAB[a].split(' ')[0]}" for w in ("W4", "W5") for a in arms]
    for ax, m in zip(axes, MODELS):
        y = 0
        for w in ws:
            for a in arms:
                o = S["order"][f"{m}|{a}"]; ef, hf = o[f"{w}|execute_first"], o[f"{w}|halt_first"]
                ax.plot([ef["pct"], hf["pct"]], [y, y], color=ACOL[a], lw=1.0, ls=ALS[a], zorder=1)
                ax.errorbar(ef["pct"], y, xerr=[[ef["pct"] - ef["lo"]], [ef["hi"] - ef["pct"]]], fmt="o", ms=3.5, color=ACOL[a],
                            mfc=ACOL[a], elinewidth=0.5, capsize=1, zorder=2)
                ax.errorbar(hf["pct"], y, xerr=[[hf["pct"] - hf["lo"]], [hf["hi"] - hf["pct"]]], fmt="o", ms=3.5, color=ACOL[a],
                            mfc="white", elinewidth=0.5, capsize=1, zorder=2)
                rows += [{"model": m, "arm": a, "wording": w, "order": od, **{k: v[k] for k in ("k", "n", "pct", "lo", "hi")}}
                         for od, v in (("execute_first", ef), ("halt_first", hf))]
                y += 1
        y += 0.5
        for w in ("W4_next", "W5_continue"):
            for a in arms:
                v = S["order"][f"{m}|{a}"][f"{w}|na"]
                ax.errorbar(v["pct"], y, xerr=[[v["pct"] - v["lo"]], [v["hi"] - v["pct"]]], fmt="D", ms=3, color=ACOL[a],
                            elinewidth=0.5, capsize=1)
                rows.append({"model": m, "arm": a, "wording": w, "order": "na", **{k: v[k] for k in ("k", "n", "pct", "lo", "hi")}})
                y += 1
        ax.axhline(8.75, color="gray", lw=0.4, ls=":")
        ax.set_xlim(-3, 103); ax.set_title(SHORT[m]); ax.set_xlabel("unsafe execution (%)"); ax.grid(axis="x", lw=0.3)
    yt = list(range(9)) + [9.5 + i for i in range(6)]
    axes[0].set_yticks(yt); axes[0].set_yticklabels(labels); axes[0].invert_yaxis()
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker="o", ls="", color="black", mfc="black", ms=3.5, label="execute named first"),
         Line2D([], [], marker="o", ls="", color="black", mfc="white", ms=3.5, label="halt named first"),
         Line2D([], [], marker="D", ls="", color="black", ms=3, label="neutral wording (W4, W5)")] + \
        [Line2D([], [], color=ACOL[a], lw=1.5, ls=ALS[a], label=ALAB[a]) for a in arms]
    fig.legend(handles=h, loc="outside lower center", ncol=3, frameon=False)
    save(fig, "fig_dumbbell", rows)


def frontier():
    """v3.1 (M7): one panel per model, so no point sits on another model's point; arm = colour, A2 hollow."""
    fig, axes = plt.subplots(1, 4, figsize=(WIDTH, 2.5), sharex=True, sharey=True)
    rows = []
    for ax, m in zip(axes, MODELS):
        P = {}
        for a in ARMS:
            f = S["frontier"][f"{m}|{a}"]; u, s_ = f["valid_executed"], f["nonvalid_not_executed"]
            P[a] = (u["pct"] + JIT[a], s_["pct"])
            dx = JIT[a]
            ax.errorbar(u["pct"] + dx, s_["pct"], xerr=[[u["pct"] - u["lo"]], [u["hi"] - u["pct"]]],
                        yerr=[[s_["pct"] - s_["lo"]], [s_["hi"] - s_["pct"]]], fmt=AMK[a], ms=5, color=ACOL[a],
                        mfc="white" if a == "A2_code_verifier" else ACOL[a], elinewidth=0.5, capsize=1, zorder=3, alpha=0.9)
            rows.append({"model": m, "arm": a, "valid_executed_k": u["k"], "valid_n": u["n"], "valid_executed_pct": u["pct"],
                         "nonvalid_not_executed_k": s_["k"], "nonvalid_n": s_["n"], "safety_pct": s_["pct"]})
        for b in ("A1_prompt_rule", "A3_structured_status"):
            if P[b] != P["A0_none"]:
                ax.annotate("", xy=P[b], xytext=P["A0_none"], arrowprops=dict(arrowstyle="->", color=ACOL[b], lw=0.7, shrinkA=3, shrinkB=3), zorder=2)
        ax.set_title(SHORT[m]); ax.set_xlim(50, 104); ax.set_ylim(15, 104); ax.grid(lw=0.3)
        ax.set_xlabel("valid executed (%)")
    axes[0].set_ylabel("non-valid not executed (%)")
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker=AMK[a], ls="", color=ACOL[a], mfc="white" if a == "A2_code_verifier" else ACOL[a], label=ALAB[a]) for a in ARMS]
    fig.legend(handles=h, loc="outside lower center", frameon=False, ncol=4, fontsize=7)
    save(fig, "fig_frontier", rows)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    tikz(); flow(); heat(); vti(); dumbbell(); frontier()
