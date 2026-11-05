"""v3.1 redraw of the four v2 bar figures (main_arm, main_variant, main_wording, pilot) at the measured text width.
Same data and the same row computations as make_figs.py (which stays unchanged); only the drawing changes:
width 6.5in (\\linewidth = 469.755pt measured in main.tex), savefig.bbox standard, Liberation Serif (TrueType),
Okabe-Ito colours plus a hatch per arm for greyscale. Writes figs/v31/<name>.pdf/.svg/.csv and checks that every
CSV equals the v2 CSV in figs/ (same k, n, rate, Wilson bounds).
Usage (from paper/figs): python redraw_v31.py"""
import csv, os, sys
import numpy as np
import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "code"))
import make_figs as mf                                            # noqa: E402  (data helpers only)
from bcharness.factorial import load, ARMS                        # noqa: E402
OUT = os.path.join(HERE, "v31"); W = 469.755 / 72.27                # 6.5in
plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none", "svg.hashsalt": "bc",
    "font.family": "serif", "font.serif": ["Liberation Serif", "DejaVu Serif"], "mathtext.fontset": "stix",
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7, "xtick.labelsize": 7,
    "ytick.labelsize": 7, "axes.spines.top": False, "axes.spines.right": False, "savefig.bbox": "standard",
    "figure.constrained_layout.use": True, "legend.frameon": False, "hatch.linewidth": 0.5})
ACOL = {"A0_none": "#000000", "A1_prompt_rule": "#0072B2", "A2_code_verifier": "#009E73", "A3_structured_status": "#D55E00"}
AHATCH = {"A0_none": None, "A1_prompt_rule": "....", "A2_code_verifier": "xxxx", "A3_structured_status": "////"}
LBL = lambda m: m.replace("-Instruct", "") + (" (bf16)" if m.startswith("Qwen2.5-3B") else "")
ALAB = mf.ALAB; VARIANTS = mf.VARIANTS; VLABEL = mf.VLABEL; CONDS = mf.CONDS; MODELS = mf.MODELS


def bars(ax, groups, series, getrows, width=0.8):
    out, m = [], len(series); x = np.arange(len(groups))
    for j, s in enumerate(series):
        vals = [mf.rate(getrows(g, s)) for g in groups]
        p = np.array([v[2] for v in vals]); lo = np.array([v[3] for v in vals]); hi = np.array([v[4] for v in vals])
        xs = x - width / 2 + width * (j + 0.5) / m
        ax.bar(xs, 100 * p, width / m * 0.92, color=ACOL[s] if s != "A0_none" else "#555555", edgecolor="white" if AHATCH[s] else None,
               hatch=AHATCH[s], linewidth=0, label=ALAB[s], zorder=2)
        ax.errorbar(xs, 100 * p, yerr=[100 * (p - lo), 100 * (hi - p)], fmt="none", ecolor="black", elinewidth=0.6, capsize=1.2, zorder=3)
        for g, v in zip(groups, vals):
            out.append({"group": g, "series": s, "k": v[0], "n": v[1], "rate": round(v[2], 4),
                        "wilson_lo": round(v[3], 4), "wilson_hi": round(v[4], 4)})
    ax.set_xticks(x); ax.set_ylim(0, 105); ax.grid(axis="y", lw=0.3, zorder=0)
    return out


def handles(arms):
    return [Patch(facecolor=ACOL[a] if a != "A0_none" else "#555555", edgecolor="white", hatch=AHATCH[a], label=ALAB[a]) for a in arms]


def save(fig, name, rows):
    fig.savefig(os.path.join(OUT, name + ".pdf"), metadata={"Creator": None, "Producer": None, "CreationDate": None})
    fig.savefig(os.path.join(OUT, name + ".svg"), metadata={"Creator": None, "Date": None}); plt.close(fig)
    mf.write_csv(os.path.join(OUT, name + ".csv"), rows)


def same(a, b):
    ra = list(csv.DictReader(open(a))); rb = list(csv.DictReader(open(b)))
    assert ra == rb, f"{a} differs from {b}"; return len(ra)


def pilot():
    p1 = load([os.path.join(ROOT, "runs/pilot/episodes.jsonl")]); p2 = load([os.path.join(ROOT, "runs/pilot-v02/episodes.jsonl")])
    order = lambda r: "halt_first" if r["draw"] % 2 else "execute_first"
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.7), gridspec_kw={"width_ratios": [2.2, 1.3]})
    arms1 = ("A0_none", "A1_prompt_rule", "A2_code_verifier")
    rows1 = bars(a, VARIANTS, arms1, lambda g, s: [r for r in p1 if r["variant"] == g and r["arm"] == s])
    a.set_xticklabels([VLABEL[v] for v in VARIANTS], rotation=30, ha="right"); a.axvline(7.5, color="gray", lw=0.6, ls=":")
    a.set_ylabel("executed (%)"); a.set_title("(a) pilot v0.1: by variant (n=30 per bar)")
    grp2 = ("execute_first|non-valid", "halt_first|non-valid", "execute_first|valid", "halt_first|valid")
    arms2 = ("A0_none", "A1_prompt_rule", "A3_structured_status")
    fam = lambda r: "valid" if r["variant"] == "valid" else "non-valid"
    rows2 = bars(b, grp2, arms2, lambda g, s: [r for r in p2 if f"{order(r)}|{fam(r)}" == g and r["arm"] == s])
    b.set_xticklabels(["non-valid, EF", "non-valid, HF", "valid, EF", "valid, HF"], rotation=30, ha="right")
    b.axvline(1.5, color="gray", lw=0.6, ls=":"); b.set_title("(b) pilot v0.2: by follow-up order")
    fig.legend(handles=handles(ARMS), ncol=4, loc="outside upper center")
    fig.savefig(os.path.join(OUT, "fig_pilot.pdf"), metadata={"Creator": None, "Producer": None, "CreationDate": None})
    fig.savefig(os.path.join(OUT, "fig_pilot.svg"), metadata={"Creator": None, "Date": None}); plt.close(fig)
    mf.write_csv(os.path.join(OUT, "fig_pilot_a.csv"), rows1); mf.write_csv(os.path.join(OUT, "fig_pilot_b.csv"), rows2)


def main():
    rows = load([os.path.join(ROOT, "runs/main", m, "episodes.jsonl") for m in MODELS])
    for r in rows: r["model"] = r["model"].split("/")[-1]
    arms = list(ARMS)
    fam = lambda r: "valid" if r["variant"] == "valid" else "non-valid"
    fig, axs = plt.subplots(1, 4, figsize=(W, 2.4), sharey=True); allrows = []
    for ax, m in zip(axs, MODELS):
        R = [r for r in rows if r["model"] == m]
        res = bars(ax, ("non-valid", "valid"), arms, lambda g, s: [r for r in R if fam(r) == g and r["arm"] == s])
        for x in res: x["model"] = m
        allrows += res; ax.set_xticklabels(["non-valid", "valid"]); ax.set_title(LBL(m))
    axs[0].set_ylabel("executed (%)"); fig.legend(handles=handles(arms), ncol=4, loc="outside upper center")
    save(fig, "fig_main_arm", allrows)
    fig, axs = plt.subplots(4, 1, figsize=(W, 7.1), sharex=True); allrows = []
    for ax, m in zip(axs, MODELS):
        R = [r for r in rows if r["model"] == m]
        res = bars(ax, VARIANTS, arms, lambda g, s: [r for r in R if r["variant"] == g and r["arm"] == s])
        for x in res: x["model"] = m
        allrows += res; ax.set_ylabel(LBL(m) + "\nexecuted (%)"); ax.axvline(7.5, color="gray", lw=0.6, ls=":")
    axs[-1].set_xticklabels([VLABEL[v] for v in VARIANTS], rotation=30, ha="right")
    fig.legend(handles=handles(arms), ncol=4, loc="outside upper center"); save(fig, "fig_main_variant", allrows)
    fig, axs = plt.subplots(4, 1, figsize=(W, 7.1), sharex=True); allrows = []
    cl = [f"{w.split('_')[0]} {o.replace('execute_first', 'exec-first').replace('halt_first', 'halt-first').replace('na', 'neutral')}" for w, o in CONDS]
    for ax, m in zip(axs, MODELS):
        R = [r for r in rows if r["model"] == m and r["variant"] != "valid"]
        res = bars(ax, list(range(8)), arms, lambda g, s: [r for r in R if (r["wording"], r["order_used"]) == CONDS[g] and r["arm"] == s])
        for x in res: x["model"] = m; x["condition"] = "/".join(CONDS[x["group"]])
        allrows += res; ax.set_ylabel(LBL(m) + "\nnon-valid exec. (%)")
    axs[-1].set_xticklabels(cl, rotation=30, ha="right")
    fig.legend(handles=handles(arms), ncol=4, loc="outside upper center"); save(fig, "fig_main_wording", allrows)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); pilot(); main()
    for n in ("fig_main_arm", "fig_main_variant", "fig_main_wording", "fig_pilot_a", "fig_pilot_b"):
        print("csv identical to v2:", n, same(os.path.join(OUT, n + ".csv"), os.path.join(HERE, n + ".csv")), "rows")
