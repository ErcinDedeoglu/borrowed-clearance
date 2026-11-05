"""Build every figure and table of the Borrowed Clearance paper from saved run outputs.
Deterministic: no sampling, no random numbers (plots use fixed layouts; seed fixed anyway).
Usage (from paper/figs):
  python make_figs.py            # diagrams + pilot figures/tables (+ main if all 4 models finished)
  python make_figs.py --main-dev ../../runs/smoke-dev --out /tmp/x   # test main plotting on dev runs only
Main-run outcome figures are GUARDED by the prereg inspection rule (prereg-2026-10-30.md): they are only produced
when runs/main/progress.log shows 'END <model> ... rc=0' for all four models. --main-dev never reads runs/main.
Definitions follow code/bcharness/factorial.py (imported): executed rate on non-valid / valid variants,
Wilson 95% intervals (bcharness.stats.wilson). A2 holds by construction and is drawn as an enforcement baseline."""
import argparse, csv, json, os, re, subprocess, sys
import numpy as np
np.random.seed(0)
import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))          # borrowed-clearance/
sys.path.insert(0, os.path.join(ROOT, "code"))
from bcharness.stats import wilson                                # noqa: E402
from bcharness.factorial import load, ARMS                        # noqa: E402
TECTONIC = os.path.abspath(os.path.join(ROOT, "..", ".tools", "tectonic"))
MODELS = ("Qwen2.5-0.5B-Instruct", "Qwen2.5-1.5B-Instruct", "SmolLM2-1.7B-Instruct", "Qwen2.5-3B-Instruct")
VARIANTS = ("none", "peer_text_claim", "doc_embedded", "floating_approval", "signed_wrong_payload",
            "signed_expired", "replayed", "unentitled_signer", "valid")
VLABEL = {"none": "none", "peer_text_claim": "peer text", "doc_embedded": "doc text", "floating_approval": "floating",
          "signed_wrong_payload": "wrong payload", "signed_expired": "expired", "replayed": "replayed",
          "unentitled_signer": "unentitled", "valid": "valid"}
ALAB = {"A0_none": "A0 none", "A1_prompt_rule": "A1 prompt rule", "A2_code_verifier": "A2 code gate*",
        "A3_structured_status": "A3 structured status"}
ACOL = {"A0_none": "#4d4d4d", "A1_prompt_rule": "#1f77b4", "A2_code_verifier": "#2ca02c", "A3_structured_status": "#ff7f0e"}
CONDS = (("W1_list", "execute_first"), ("W1_list", "halt_first"), ("W2_question", "execute_first"),
         ("W2_question", "halt_first"), ("W3_options", "execute_first"), ("W3_options", "halt_first"),
         ("W4_next", "na"), ("W5_continue", "na"))
plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
                     "legend.fontsize": 7, "xtick.labelsize": 7, "ytick.labelsize": 7, "pdf.fonttype": 42,
                     "axes.spines.top": False, "axes.spines.right": False, "savefig.bbox": "tight",
                     "svg.hashsalt": "bc", "pdf.compression": 6})
META = {"Creator": "make_figs.py", "Producer": None, "CreationDate": None}


def kn(rows, pred):
    return sum(1 for r in rows if pred(r)), len(rows)


def rate(rows):
    k, n = kn(rows, lambda r: r["executed"])
    lo, hi = wilson(k, n) if n else (float("nan"),) * 2
    return k, n, (k / n if n else float("nan")), lo, hi


def bars(ax, groups, series, getrows, colors, labels, width=0.8):
    """groups on x; one bar per series with Wilson 95% error bars. Returns list of csv rows."""
    out, m = [], len(series)
    x = np.arange(len(groups))
    for j, s in enumerate(series):
        vals = [rate(getrows(g, s)) for g in groups]
        p = np.array([v[2] for v in vals]); lo = np.array([v[3] for v in vals]); hi = np.array([v[4] for v in vals])
        xs = x - width / 2 + width * (j + 0.5) / m
        ax.bar(xs, 100 * p, width / m * 0.92, color=colors[s], label=labels[s], zorder=2)
        ax.errorbar(xs, 100 * p, yerr=[100 * (p - lo), 100 * (hi - p)], fmt="none", ecolor="black", elinewidth=0.6,
                    capsize=1.2, zorder=3)
        for g, v in zip(groups, vals):
            out.append({"group": g, "series": s, "k": v[0], "n": v[1], "rate": round(v[2], 4),
                        "wilson_lo": round(v[3], 4), "wilson_hi": round(v[4], 4)})
    ax.set_xticks(x); ax.set_ylim(0, 105); ax.grid(axis="y", lw=0.3, zorder=0)
    return out


def write_csv(path, rows):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


def pct(k, n):
    lo, hi = wilson(k, n)
    return f"{k}/{n} & {100*k/n:.0f} & [{100*lo:.0f}, {100*hi:.0f}]"


# ---------------------------------------------------------------- diagrams
def diagrams(out):
    for name in ("fig_harness", "fig_design"):
        subprocess.run([TECTONIC, "-X", "compile", "--outdir", out, os.path.join(HERE, "tikz", name + ".tex")],
                       check=True, capture_output=True)
        print("wrote", os.path.join(out, name + ".pdf"))


# ---------------------------------------------------------------- pilot
def pilot(out):
    p1 = load([os.path.join(ROOT, "runs/pilot/episodes.jsonl")])
    p2 = load([os.path.join(ROOT, "runs/pilot-v02/episodes.jsonl")])
    order = lambda r: "halt_first" if r["draw"] % 2 else "execute_first"     # v0.2 counterbalance (agent.py)
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.4), gridspec_kw={"width_ratios": [2.2, 1.3]})
    arms1 = ("A0_none", "A1_prompt_rule", "A2_code_verifier")
    rows1 = bars(a, VARIANTS, arms1, lambda g, s: [r for r in p1 if r["variant"] == g and r["arm"] == s], ACOL, ALAB)
    a.set_xticklabels([VLABEL[v] for v in VARIANTS], rotation=30, ha="right")
    a.axvline(7.5, color="gray", lw=0.6, ls=":")
    a.set_ylabel("executed (%)"); a.set_title("(a) pilot v0.1: by variant (n=30 per bar)")
    grp2 = ("execute_first|non-valid", "halt_first|non-valid", "execute_first|valid", "halt_first|valid")
    arms2 = ("A0_none", "A1_prompt_rule", "A3_structured_status")
    fam = lambda r: "valid" if r["variant"] == "valid" else "non-valid"
    rows2 = bars(b, grp2, arms2, lambda g, s: [r for r in p2 if f"{order(r)}|{fam(r)}" == g and r["arm"] == s], ACOL, ALAB)
    b.set_xticklabels(["non-valid, EF", "non-valid, HF", "valid, EF", "valid, HF"], rotation=30, ha="right")
    b.axvline(1.5, color="gray", lw=0.6, ls=":")
    b.set_title("(b) pilot v0.2: by follow-up order")
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=ACOL[x], label=ALAB[x]) for x in ARMS], ncol=4, frameon=False,
               loc="upper center", bbox_to_anchor=(0.5, 1.07))
    fig.savefig(os.path.join(out, "fig_pilot.pdf"), metadata=META); plt.close(fig)
    write_csv(os.path.join(out, "fig_pilot_a.csv"), rows1); write_csv(os.path.join(out, "fig_pilot_b.csv"), rows2)
    print("wrote fig_pilot.pdf, fig_pilot_a.csv, fig_pilot_b.csv")
    # table: pilot summary (booktabs)
    nv = lambda r: r["variant"] != "valid"; v = lambda r: r["variant"] == "valid"
    L = [r"% generated by paper/figs/make_figs.py from runs/pilot and runs/pilot-v02 -- do not edit by hand",
         r"\begin{tabular}{@{}llrrr rrr@{}}", r"\toprule",
         r" & & \multicolumn{3}{c}{non-valid executed} & \multicolumn{3}{c}{valid executed} \\",
         r"\cmidrule(lr){3-5}\cmidrule(l){6-8}",
         r"Pilot & Arm & $k/n$ & \% & 95\% CI & $k/n$ & \% & 95\% CI \\", r"\midrule"]
    for a_ in arms1:
        R = [r for r in p1 if r["arm"] == a_]
        L.append(f"v0.1 & {ALAB[a_]} & {pct(*kn([r for r in R if nv(r)], lambda r: r['executed']))} & "
                 f"{pct(*kn([r for r in R if v(r)], lambda r: r['executed']))} \\\\")
    L.append(r"\midrule")
    for o in ("execute_first", "halt_first"):
        for a_ in arms2:
            R = [r for r in p2 if r["arm"] == a_ and order(r) == o]
            L.append(f"v0.2 {o.replace('_', '-')} & {ALAB[a_]} & {pct(*kn([r for r in R if nv(r)], lambda r: r['executed']))} & "
                     f"{pct(*kn([r for r in R if v(r)], lambda r: r['executed']))} \\\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    open(os.path.join(out, "tab_pilot.tex"), "w").write("\n".join(L) + "\n")
    # attempted vs executed for A2 (enforcement baseline, by construction)
    R = [r for r in p1 if r["arm"] == "A2_code_verifier"]
    with open(os.path.join(out, "pilot_a2_baseline.json"), "w") as fh:
        json.dump({"A2_nonvalid_executed": kn([r for r in R if nv(r)], lambda r: r["executed"]),
                   "A2_attempted_all": kn(R, lambda r: r["attempted_execute"]),
                   "A2_valid_executed": kn([r for r in R if v(r)], lambda r: r["executed"]),
                   "note": "holds by construction; not a finding"}, fh, indent=1)
    print("wrote tab_pilot.tex, pilot_a2_baseline.json")


# ---------------------------------------------------------------- main (guarded)
def finished_models(progress):
    done = set()
    for line in open(progress):
        m = re.match(r"END (\S+) attempt \d+ rc=0 rows=1728", line)
        if m: done.add(m.group(1))
    return done


def main_figs(run_dir, out, tag=""):
    paths = [os.path.join(run_dir, m, "episodes.jsonl") for m in MODELS if os.path.exists(os.path.join(run_dir, m, "episodes.jsonl"))]
    rows = load(paths)
    for r in rows: r["model"] = r["model"].split("/")[-1]
    models = [m for m in MODELS if any(r["model"] == m for r in rows)]
    arms = [a for a in ARMS if any(r["arm"] == a for r in rows)]
    nm = len(models)
    # Fig: executed by arm (non-valid and valid), one panel per model
    fig, axs = plt.subplots(1, nm, figsize=(1.9 * nm + 0.4, 2.1), sharey=True, squeeze=False)
    allrows = []
    for ax, m in zip(axs[0], models):
        R = [r for r in rows if r["model"] == m]
        fam = lambda r: "valid" if r["variant"] == "valid" else "non-valid"
        res = bars(ax, ("non-valid", "valid"), arms, lambda g, s: [r for r in R if fam(r) == g and r["arm"] == s], ACOL, ALAB)
        for x in res: x["model"] = m
        allrows += res; ax.set_xticklabels(["non-valid", "valid"]); ax.set_title(m.replace("-Instruct", ""))
    axs[0][0].set_ylabel("executed (%)")
    axs[0][0].legend(ncol=4, frameon=False, loc="lower left", bbox_to_anchor=(0, 1.1))
    fig.savefig(os.path.join(out, f"fig_main_arm{tag}.pdf"), metadata=META); plt.close(fig)
    write_csv(os.path.join(out, f"fig_main_arm{tag}.csv"), allrows)
    # Fig: executed by variant x arm, one row per model
    fig, axs = plt.subplots(nm, 1, figsize=(7.0, 1.7 * nm + 0.3), sharex=True, squeeze=False)
    allrows = []
    for ax, m in zip(axs[:, 0], models):
        R = [r for r in rows if r["model"] == m]
        res = bars(ax, VARIANTS, arms, lambda g, s: [r for r in R if r["variant"] == g and r["arm"] == s], ACOL, ALAB)
        for x in res: x["model"] = m
        allrows += res; ax.set_ylabel(m.replace("-Instruct", "") + "\nexecuted (%)"); ax.axvline(7.5, color="gray", lw=0.6, ls=":")
    axs[-1, 0].set_xticklabels([VLABEL[v] for v in VARIANTS], rotation=30, ha="right")
    axs[0, 0].legend(ncol=4, frameon=False, loc="lower left", bbox_to_anchor=(0, 1.02))
    fig.savefig(os.path.join(out, f"fig_main_variant{tag}.pdf"), metadata=META); plt.close(fig)
    write_csv(os.path.join(out, f"fig_main_variant{tag}.csv"), allrows)
    # Fig: wording effect: non-valid executed by condition x arm, one panel per model
    fig, axs = plt.subplots(nm, 1, figsize=(7.0, 1.7 * nm + 0.3), sharex=True, squeeze=False)
    allrows = []
    cl = [f"{w.split('_')[0]} {o.replace('execute_first', 'exec-first').replace('halt_first', 'halt-first').replace('na', 'neutral')}" for w, o in CONDS]
    for ax, m in zip(axs[:, 0], models):
        R = [r for r in rows if r["model"] == m and r["variant"] != "valid"]
        res = bars(ax, list(range(8)), arms, lambda g, s: [r for r in R if (r["wording"], r["order_used"]) == CONDS[g] and r["arm"] == s], ACOL, ALAB)
        for x in res: x["model"] = m; x["condition"] = "/".join(CONDS[x["group"]])
        allrows += res; ax.set_ylabel(m.replace("-Instruct", "") + "\nnon-valid exec. (%)")
    axs[-1, 0].set_xticklabels(cl, rotation=30, ha="right")
    axs[0, 0].legend(ncol=4, frameon=False, loc="lower left", bbox_to_anchor=(0, 1.02))
    fig.savefig(os.path.join(out, f"fig_main_wording{tag}.pdf"), metadata=META); plt.close(fig)
    write_csv(os.path.join(out, f"fig_main_wording{tag}.csv"), allrows)
    # Table: P1 per model and arm (booktabs)
    L = [f"% generated by paper/figs/make_figs.py from {os.path.relpath(run_dir, ROOT)} -- do not edit by hand",
         r"\begin{tabular}{@{}ll rrr rrr r@{}}", r"\toprule",
         r" & & \multicolumn{3}{c}{non-valid executed} & \multicolumn{3}{c}{valid executed} & parse fail \\",
         r"\cmidrule(lr){3-5}\cmidrule(lr){6-8}", r"Model & Arm & $k/n$ & \% & 95\% CI & $k/n$ & \% & 95\% CI & $k/n$ \\", r"\midrule"]
    for m in models:
        for a_ in arms:
            R = [r for r in rows if r["model"] == m and r["arm"] == a_]
            pf = kn(R, lambda r: r["parse_fail"])
            L.append(f"{m.replace('-Instruct', '')} & {ALAB[a_]} & {pct(*kn([r for r in R if r['variant'] != 'valid'], lambda r: r['executed']))} & "
                     f"{pct(*kn([r for r in R if r['variant'] == 'valid'], lambda r: r['executed']))} & {pf[0]}/{pf[1]} \\\\")
        L.append(r"\midrule" if m != models[-1] else r"\bottomrule")
    L.append(r"\end{tabular}")
    open(os.path.join(out, f"tab_main{tag}.tex"), "w").write("\n".join(L) + "\n")
    print("wrote main figures/tables", tag, "models:", models)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=HERE)
    ap.add_argument("--main-dev", help="dev run dir (e.g. ../../runs/smoke-dev) to test main plotting; never runs/main")
    ap.add_argument("--skip-diagrams", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.main_dev:
        assert "runs/main" not in os.path.abspath(a.main_dev), "--main-dev must not point at runs/main"
        main_figs(a.main_dev, a.out, tag="_dev"); sys.exit(0)
    if not a.skip_diagrams: diagrams(a.out)
    pilot(a.out)
    prog = os.path.join(ROOT, "runs/main/progress.log")
    done = finished_models(prog) if os.path.exists(prog) else set()
    if set(MODELS) <= done:
        main_figs(os.path.join(ROOT, "runs/main"), a.out)
    else:
        print("main-run figures NOT built (prereg inspection rule): finished =", sorted(done),
              "waiting for", sorted(set(MODELS) - done))
