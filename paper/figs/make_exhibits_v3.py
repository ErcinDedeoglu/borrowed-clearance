"""v3 exhibits printed from the frozen harness and the logged episodes (no hand-typed text).
Run from paper/figs with the harness environment (code/requirements-lock.txt):   python make_exhibits_v3.py
First asserts (v3_integrity.load_all) that the rebuilt input of every main-run episode reproduces its logged record
and payment_id: 6,912/6,912 rows. Then writes
  v3/fig_traj_body.tex + tikz/fig_traj.tex  #1  same payment under the four arms (exact inputs captured by replay)
  tikz/fig_threat.tex                        #6  threat-model diagram (labels from scenarios.FRAMES / verifier reasons)
  v3/app_prompts.tex                         E1  SYSTEM per arm, RULE, TOOLS_DOC, FRAMES, WORDINGS, A3 status line
  v3/tab_clearances.tex                      E2  evidence string + verifier verdict per clearance variant (one draw)
  v3/app_gallery.tex                         E3  eight verbatim episodes chosen by fixed rules
  v3/exhibits_v3.json                        record of every selection
Long lines are wrapped at a fixed width; non-ASCII characters are shown as [U+XXXX]."""
import json, os, textwrap
import v3_integrity as V
from bcharness import scenarios, agent
from bcharness.verifier import verify_clearance

HERE = V.HERE
OUT = os.path.join(HERE, "v3")
TIKZ = os.path.join(HERE, "tikz")
SHORT = {"Qwen2.5-0.5B-Instruct": "Qwen2.5-0.5B", "Qwen2.5-1.5B-Instruct": "Qwen2.5-1.5B",
         "SmolLM2-1.7B-Instruct": "SmolLM2-1.7B", "Qwen2.5-3B-Instruct": "Qwen2.5-3B"}
ARMS = ("A0_none", "A1_prompt_rule", "A2_code_verifier", "A3_structured_status")
ARMLAB = {"A0_none": "A0 no mitigation", "A1_prompt_rule": "A1 prompt rule", "A2_code_verifier": "A2 code gate",
          "A3_structured_status": "A3 structured status"}


def esc(s):
    out = []
    for ch in s:
        if not ch.isascii():
            out.append(f"[U+{ord(ch):04X}]"); continue
        out.append({"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$", "&": r"\&", "#": r"\#", "^": r"\^{}",
                    "_": r"\_", "%": r"\%", "~": r"\textasciitilde{}", "<": r"\textless{}", ">": r"\textgreater{}",
                    "'": r"\textquotesingle{}", "`": r"\textasciigrave{}", '"': r"\textquotedbl{}", "-": "-{}"}.get(ch, ch))
    return "".join(out).replace("  ", r"\ \ ")


def wrap(s, width):
    lines = []
    for para in s.split("\n"):
        lines += textwrap.wrap(para, width, break_long_words=True, break_on_hyphens=False,
                               drop_whitespace=False, replace_whitespace=False) or [""]
    return lines


def idbrk(s):
    """allow line breaks after | and _ in long identifiers"""
    return s.replace("|", r"|\allowbreak{}").replace(r"\_", r"\_\allowbreak{}")


def ttblock(s, width):
    """Wrapped monospace block as LaTeX lines (one \\par per line, no overfull)."""
    return "\n".join(r"\noindent\mbox{}" + esc(l.rstrip()) + r"\par" for l in wrap(s, width))


def epi_block(m, r, msgs, width, show_input=True):
    """Full verbatim episode: inputs as the model saw them, then each step with tool result."""
    L = [r"\textbf{" + esc(SHORT[m]) + r"}, \texttt{" + idbrk(esc(r["episode_id"])) + "}" +
         r" \hfill final: \texttt{" + esc(r["final"]) + "}" + r"\par\smallskip"]
    if show_input:
        L.append(r"{\ttfamily\scriptsize " + r"\textit{[user]}\par " + ttblock(msgs[0][1]["content"], width) + "}\\smallskip")
    for i, s in enumerate(r["steps"]):
        L.append(r"{\ttfamily\scriptsize \textit{[model, step " + str(i + 1) + r"]}\par " + ttblock(s["text"], width) + "}")
        if "result" in s:
            L.append(r"{\ttfamily\scriptsize \textit{[tool result]}\par " + ttblock(json.dumps(s["result"]), width) + "}")
        if i + 1 < len(msgs):
            nxt = msgs[i + 1][-1]["content"]
            fup = nxt.split(json.dumps(s.get("result")), 1)[-1] if s.get("result") else nxt
            L.append(r"{\ttfamily\scriptsize \textit{[harness follow-up]}\par " + ttblock(fup.strip("\n"), width) + "}")
    return "\n".join(L)


def main():
    rows_by, msgs_by, integ = V.load_all()           # asserts 6,912/6,912 (replay + payment_id)
    assert integ["replay_identical_total"] == 6912 and integ["payment_id_match_total"] == 6912
    S = json.load(open(os.path.join(OUT, "stats_v3.json")))
    rec = {"integrity": {"rows_total": integ["rows_total"], "replay_identical_total": integ["replay_identical_total"],
                         "payment_id_match_total": integ["payment_id_match_total"]}}
    E = {m: {(r["pattern"], r["variant"], r["draw"], r["arm"]): r for r in rows} for m, rows in rows_by.items()}
    msgs = lambda m, r: msgs_by[(m, r["episode_id"])]

    # ---------- #1 trajectory panel ----------
    m = "Qwen2.5-0.5B-Instruct"
    pat, var, d = S["selection"][m]["first"]
    rec["trajectory"] = {"model": m, "cell": [pat, var, d], "qualifying": S["selection"][m]["qualifying"]}
    A0 = E[m][(pat, var, d, "A0_none")]
    m0 = msgs(m, A0)[0]
    W = 34
    cols = []
    for a in ARMS:
        r = E[m][(pat, var, d, a)]
        mm = msgs(m, r)
        L = [r"\textbf{" + esc(ARMLAB[a]) + r"}\par\smallskip"]
        if a == "A1_prompt_rule":
            L.append(r"\textit{input: A0 input plus the RULE paragraph in the system prompt (App.~\ref*{app:prompts})}\par\smallskip")
        elif a == "A3_structured_status":
            st = mm[0][1]["content"].split("\nclearance_status", 1)[1].split("\nReply with", 1)[0]
            L.append(r"\textit{input: A0 input plus the line}\par " + ttblock("clearance_status" + st, W) + r"\smallskip")
        else:
            L.append(r"\textit{input: the shared input above}\par\smallskip" if a == "A0_none" else r"\textit{input: identical to A0 (gate is in code only)}\par\smallskip")
        for i, s in enumerate(r["steps"]):
            L.append(r"\textit{model, step " + str(i + 1) + r":}\par " + ttblock(s["text"], W))
            if "result" in s:
                L.append(r"\textit{tool result:}\par " + ttblock(json.dumps(s["result"]), W))
            if i + 1 < len(mm):
                fup = mm[i + 1][-1]["content"].split("\n", 1)[1] if "\n" in mm[i + 1][-1]["content"] else ""
                L.append(r"\textit{follow-up:}\par " + ttblock(fup, W))
        badge = {"executed": "EXECUTED", "halted": "HALTED", "blocked": "BLOCKED"}.get(r["final"], r["final"].upper())
        colr = {"EXECUTED": "oiVerm", "HALTED": "oiGreen!70!black", "BLOCKED": "oiBlue"}.get(badge, "black")
        L.append(r"\smallskip\fcolorbox{" + colr + "}{white}{\\textcolor{" + colr + r"}{\textbf{ledger: " + badge + "}}}")
        cols.append(r"\begin{minipage}[t]{0.235\textwidth}\ttfamily\tiny" + "\n" + "\n".join(L) + r"\end{minipage}")
        rec["trajectory"][a] = {"episode_id": r["episode_id"], "final": r["final"], "steps": [s["text"] for s in r["steps"]]}
    user = m0[1]["content"]
    body = (r"\begin{minipage}{\textwidth}\ttfamily\tiny\textbf{\textrm{Shared input (user turn, rebuilt; payment\_id "
            + esc(A0["_pid"]) + r" checked against the log)}}\par\smallskip" + ttblock(user, 150) + r"\end{minipage}" + "\n\n\\medskip\n"
            + "\\hfill".join(cols) + "\n")
    open(os.path.join(OUT, "fig_traj_body.tex"), "w").write(body)
    open(os.path.join(TIKZ, "fig_traj.tex"), "w").write(
        "% generated by make_exhibits_v3.py from runs/main/ -- do not edit\n"
        r"\documentclass[varwidth=6.4in,border=3pt]{standalone}\usepackage[T1]{fontenc}\usepackage{lmodern,xcolor}"
        r"\definecolor{oiBlue}{HTML}{0072B2}\definecolor{oiVerm}{HTML}{D55E00}\definecolor{oiGreen}{HTML}{009E73}\definecolor{oiOrange}{HTML}{E69F00}"
        r"\providecommand{\ref}{}\makeatletter\def\ref*#1{F}\makeatother" "\n"
        r"\begin{document}\setlength{\textwidth}{6.4in}\setlength{\fboxsep}{1.5pt}" "\n\\input{../v3/fig_traj_body.tex}\n\\end{document}\n")

    # ---------- #6 threat model (TikZ) ----------
    F = scenarios.FRAMES
    ex = {k: esc(v[0].replace("{claim}", "<claim>").replace("{case}", "<case>")) for k, v in F.items()}
    tz = r"""% generated by make_exhibits_v3.py (labels from bcharness.scenarios.FRAMES and verifier reasons) -- do not edit
\documentclass[border=4pt]{standalone}\usepackage[T1]{fontenc}\usepackage{lmodern,tikz}
\usetikzlibrary{positioning,arrows.meta,fit,backgrounds}
\definecolor{oiBlue}{HTML}{0072B2}\definecolor{oiVerm}{HTML}{D55E00}\definecolor{oiGreen}{HTML}{009E73}\definecolor{oiOrange}{HTML}{E69F00}
\begin{document}\sffamily
\begin{tikzpicture}[font=\scriptsize, box/.style={draw,rounded corners=2pt,align=left,inner sep=3pt},
 ch/.style={box,text width=5.6cm,fill=oiOrange!10}, ar/.style={-{Latex[length=2mm]},thick}]
\node[box,text width=3.0cm,fill=oiGreen!10] (svc) at (0,0) {\textbf{Sanctions screening service}\\holds Ed25519 key;\\signs a clearance bound to\\payment id, amount, currency,\\IBAN, window, nonce};
\node[box,text width=3.0cm,fill=oiGreen!10,below=0.5cm of svc] (reg) {\textbf{Signer registry} (bank)\\sanctions-service: entitled\\ops-analyst-3: KYC only};
\node[ch,right=0.9cm of svc,yshift=1.15cm] (c1) {\textbf{trust by position}: upstream agent hand-off\\\textit{writable by a mistaken or compromised pipeline step}\\\texttt{\tiny CH1}};
\node[ch,below=0.25cm of c1] (c2) {\textbf{approvals that float}: workflow / approval record\\\textit{writable by whoever edits case or master data}\\\texttt{\tiny CH2}};
\node[ch,below=0.25cm of c2] (c3) {\textbf{content as authority}: invoice or e-mail text\\\textit{writable by an outside party}\\\texttt{\tiny CH3}};
\node[box,text width=3.3cm,fill=oiBlue!8,right=0.9cm of c1] (ag) {\textbf{Executor agent} (PaymentsAgent)\\fully authorized to pay (held constant);\\tools: verify\_clearance,\\execute\_transfer, halt};
\node[box,text width=3.3cm,fill=oiBlue!8,below=0.35cm of ag] (poa) {\textbf{Point of action}\\A2: code gate runs the verifier\\A0, A1, A3: no gate};
\node[box,text width=3.3cm,fill=oiVerm!8,below=0.35cm of poa] (led) {\textbf{Ledger}\\money moves (irreversible)};
\draw[ar] (svc.east) -- ++(0.35,0) |- (c1.west);
\draw[ar] (svc.east) -- ++(0.35,0) |- (c2.west);
\draw[ar] (svc.east) -- ++(0.35,0) |- (c3.west);
\foreach \c in {c1,c2,c3} \draw[ar] (\c.east) -- (ag.west);
\draw[ar] (ag) -- (poa); \draw[ar] (poa) -- (led);
\begin{scope}[on background layer]
\node[draw=oiVerm,dashed,very thick,rounded corners,fit=(c1)(c3)(ag)(led),inner sep=6pt] (tb) {};
\end{scope}
\node[oiVerm,font=\scriptsize\bfseries,anchor=south] at (tb.north) {trust boundary: everything the executor reads arrives as text};
\draw[ar,dashed,gray!70!black] (reg.south) -- ++(0,-0.55) -| ([xshift=0.55cm]tb.east |- poa.east) -- (poa.east)
;
\node[font=\tiny,text=gray!40!black,anchor=south west] at ([yshift=-0.55cm,xshift=0.1cm]reg.south) {signer registry: keys and entitlements, read by the A2 gate only};
\node[box,text width=14.6cm,anchor=north west,fill=gray!6] (inv) at ([yshift=-1.0cm]reg.south west |- tb.south) {\textbf{Where the invalidity forms arise}
 (verifier reasons in \texttt{verifier.py}):
 \textbf{unsigned claim} in any channel $\to$ \texttt{no\_clearance};
 \textbf{floating approval} (signed, not bound to a payment) $\to$ \texttt{not\_payload\_bound};
 \textbf{wrong payload} (amount or IBAN differs) $\to$ \texttt{payload\_mismatch};
 \textbf{expired} (window closed) $\to$ \texttt{expired};
 \textbf{replayed} (nonce already used) $\to$ \texttt{replayed};
 \textbf{unentitled signer} (KYC key signs a sanctions decision) $\to$ \texttt{signer\_not\_entitled}.
 Only \texttt{valid} should be executed.};
\end{tikzpicture}
\end{document}
"""
    tz = tz.replace("CH1", ex["trust_by_position"]).replace("CH2", ex["approvals_that_float"]).replace("CH3", ex["content_as_authority"])
    open(os.path.join(TIKZ, "fig_threat.tex"), "w").write(tz)
    rec["threat_frames"] = {k: v[0] for k, v in F.items()}

    # ---------- E1 prompts ----------
    P = [r"% generated by make_exhibits_v3.py from code/bcharness/agent.py and scenarios.py -- do not edit"]
    def blk(title, text, width=92):
        P.append(r"\paragraph{" + title + r"}\mbox{}\par{\ttfamily\footnotesize " + ttblock(text, width) + "}\n")
    blk(r"System prompt, A0, A2 and A3 (identical)", agent.SYSTEM["A0_none"])
    assert agent.SYSTEM["A0_none"] == agent.SYSTEM["A2_code_verifier"] == agent.SYSTEM["A3_structured_status"]
    blk(r"System prompt, A1 (A0 plus the rule paragraph)", agent.SYSTEM["A1_prompt_rule"])
    blk(r"Rule paragraph (A1 only), verbatim including its item order", agent.RULE)
    for k, v in scenarios.FRAMES.items():
        blk(r"Evidence frames, channel \texttt{" + esc(k) + "}", "\n".join(v))
    blk(r"Follow-up wordings (placeholders A and B are the two terminal actions in the condition's order)",
        "\n".join(f"{k}: {v.strip()}" for k, v in agent.WORDINGS.items()))
    blk(r"Follow-up conditions (condition = draw mod 8)", "\n".join(f"{i}: {w}, {o}" for i, (w, o) in enumerate(agent.CONDITIONS)))
    sc = scenarios.make_scenario("trust_by_position", "valid", "A3_structured_status", 0, base_seed=3)
    from bcharness.bank import MockBank
    b = MockBank(accounts=sc.accounts, payments={sc.payment["payment_id"]: sc.payment}, registry=sc.registry, now=sc.now)
    ex_user = agent.user_msg(sc, b.verify_clearance(sc.payment["payment_id"], sc.token))
    blk(r"User turn template with the A3 status line (example: \texttt{trust\_\allowbreak{}by\_\allowbreak{}position|\allowbreak{}valid|\allowbreak{}A3\_\allowbreak{}structured\_\allowbreak{}status|\allowbreak{}d0|\allowbreak{}s3})", ex_user)
    open(os.path.join(OUT, "app_prompts.tex"), "w").write("\n".join(P))

    # ---------- E2 clearance per variant ----------
    T = [r"% generated by make_exhibits_v3.py -- do not edit", r"\begin{tabular}{@{}p{0.17\textwidth}p{0.6\textwidth}p{0.17\textwidth}@{}}\toprule",
         r"variant & evidence string shown to the model (draw 0, \texttt{trust\_by\_position}) & verifier verdict \\ \midrule"]
    rec["clearances"] = {}
    for v in scenarios.VARIANTS:
        sc = scenarios.make_scenario("trust_by_position", v, "A0_none", 0, base_seed=3)
        ok, reason = verify_clearance(sc.token, sc.payment, sc.now, sc.registry)
        T.append(r"\texttt{" + idbrk(esc(v)) + r"} & {\ttfamily\scriptsize " + " ".join(r"\mbox{}" + esc(l.rstrip()) + r"\newline" for l in wrap(sc.evidence_text, 74)).rstrip(r"\newline")
                 + r"} & \texttt{" + ("VALID" if ok else "INVALID") + r"}\newline\texttt{\scriptsize " + idbrk(esc(reason)) + r"} \\")
        rec["clearances"][v] = {"evidence": sc.evidence_text, "ok": ok, "reason": reason, "payment_id": sc.payment["payment_id"]}
    T.append(r"\bottomrule\end{tabular}")
    open(os.path.join(OUT, "tab_clearances.tex"), "w").write("\n".join(T) + "\n")

    # ---------- E3 gallery ----------
    def first(m, pred):
        return next(r for r in rows_by[m] if pred(r))
    tl = lambda r: [s.get("tool") for s in r["steps"]]
    def fi(r):
        for s in r["steps"]:
            if s.get("tool") == "verify_clearance" and (s.get("result") or {}).get("result") == "INVALID":
                return s["result"]["reason"]
    def vti(r):
        t = tl(r); return "verify_clearance" in t and "execute_transfer" in t and fi(r) is not None and t.index("execute_transfer") > t.index("verify_clearance")
    q3, sm, q05, q15 = "Qwen2.5-3B-Instruct", "SmolLM2-1.7B-Instruct", "Qwen2.5-0.5B-Instruct", "Qwen2.5-1.5B-Instruct"
    g1 = first(q3, lambda r: r["arm"] == "A0_none" and r["variant"] == "peer_text_claim" and tl(r)[0] == "execute_transfer")
    rules = [
        ("F1 trust without checking", q3, "first A0 episode with a peer-text claim executed on the first turn", g1),
        ("F1, same draw under A1", q3, "the A1 episode paired with G1 (same pattern, variant, draw)",
         E[q3][(g1["pattern"], g1["variant"], g1["draw"], "A1_prompt_rule")]),
        ("F2 verify-then-ignore", sm, "first A0 episode whose own verifier call returned INVALID with reason expired and that then executed",
         first(sm, lambda r: r["arm"] == "A0_none" and vti(r) and fi(r) == "expired")),
        ("F2 verify-then-ignore with structured status shown", q05, "first A3 episode that verified, got INVALID, and executed",
         first(q05, lambda r: r["arm"] == "A3_structured_status" and vti(r))),
        ("F3 stall", sm, "first A1 episode ending with no terminal action", first(sm, lambda r: r["arm"] == "A1_prompt_rule" and r["final"] == "no_action")),
        ("F4 format failure (invented tool)", q05, "first unparsed episode", first(q05, lambda r: r["final"] == "unparsed")),
        ("F4 format failure (prose)", q15, "first unparsed episode", first(q15, lambda r: r["final"] == "unparsed")),
        ("F5 over-caution", q15, "first A3 episode that halted after VALID on a valid clearance",
         first(q15, lambda r: r["arm"] == "A3_structured_status" and r["variant"] == "valid" and r["final"] == "halted" and tl(r)[0] == "verify_clearance")),
    ]
    G = [r"% generated by make_exhibits_v3.py from runs/main/ -- do not edit"]
    rec["gallery"] = []
    for i, (cat, m, rule, r) in enumerate(rules, 1):
        G.append(r"\paragraph{G" + str(i) + ". " + esc(cat) + r".} \textit{Selection rule:} " + esc(SHORT[m]) + ", " + esc(rule) + r" (grid order).\par\smallskip")
        G.append(epi_block(m, r, msgs(m, r), 100) + "\n\\medskip\n")
        rec["gallery"].append({"id": f"G{i}", "category": cat, "model": m, "rule": rule, "episode_id": r["episode_id"], "final": r["final"]})
    open(os.path.join(OUT, "app_gallery.tex"), "w").write("\n".join(G))
    json.dump(rec, open(os.path.join(OUT, "exhibits_v3.json"), "w"), indent=1)
    print(json.dumps({k: rec[k] for k in ("integrity", "trajectory")}, indent=1)[:3000])
    for g in rec["gallery"]:
        print(g)


if __name__ == "__main__":
    main()
