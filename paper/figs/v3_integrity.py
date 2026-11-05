"""v3 input integrity: rebuild every main-run episode input from the frozen harness and check it against the log.
Imported by stats_v3.py and make_exhibits_v3.py (both run with the harness environment, code/requirements-lock.txt).
Checks (all asserted, nothing printed by hand):
  * 4 models x 1,728 rows = 6,912 rows; episode_ids unique and equal to the pre-registered grid
  * code_sha256 of code/bcharness (run.code_hash) unchanged and equal in every manifest; factorial.py sha unchanged
  * runs/main/progress.log has 'END <model> ... rc=0 rows=1728' for every model
  * replay: for every row, make_scenario(..., base_seed=3) + the logged model texts fed back through the unchanged
    run_episode reproduce the logged record field for field (so the rebuilt input, the verifier results and the
    scorer all match); the exact chat messages each model saw are captured for the exhibits
  * payment id: the rebuilt payment_id is the one in the model input and in every logged tool/ledger result;
    ids the model itself wrote (PX-dddd) are compared too and any model typo is listed (not an input mismatch)."""
import hashlib, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "code"))
from bcharness import scenarios, agent, run as bcrun          # noqa: E402

MODELS = ("Qwen2.5-0.5B-Instruct", "Qwen2.5-1.5B-Instruct", "SmolLM2-1.7B-Instruct", "Qwen2.5-3B-Instruct")
CODE_SHA = "fd4df50a8f3d6bd29a8e2b9a05e58220d01b0c4657ad3d25c10b35f2a8154e17"
FACTORIAL_SHA = "0ad1d21e5b9d2fadc1b4155034398a008aff57396b0bb90b8ae4a7f7593e8548"
PID_RE = re.compile(r"PX-\d+")


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load_all():
    """Return (rows_by_model, msgs_by_episode_key, report dict). Asserts every check."""
    rep = {"code_sha256_now": bcrun.code_hash(), "factorial_sha256_now": sha256(os.path.join(ROOT, "code/bcharness/factorial.py"))}
    assert rep["code_sha256_now"] == CODE_SHA, rep
    assert rep["factorial_sha256_now"] == FACTORIAL_SHA, rep
    prog = open(os.path.join(ROOT, "runs/main/progress.log")).read()
    grid_ids = {sc.episode_id for sc in scenarios.grid(16, 3, arms=scenarios.ALL_ARMS)}
    assert len(grid_ids) == 1728
    rows_by, msgs_by, per = {}, {}, {}
    for m in MODELS:
        assert re.search(rf"END {re.escape(m)} attempt \d+ rc=0 rows=1728", prog), m
        p = os.path.join(ROOT, "runs/main", m, "episodes.jsonl")
        man = json.load(open(os.path.join(ROOT, "runs/main", m, "manifest.json")))
        assert man["code_sha256"] == CODE_SHA and man["base_seed"] == 3 and man["followup_order"] == "factorial", m
        rows = [json.loads(l) for l in open(p)]
        ids = [r["episode_id"] for r in rows]
        assert len(rows) == 1728 and len(set(ids)) == 1728 and set(ids) == grid_ids, m
        replay_ok, pid_mention_rows, pid_bad, typo = 0, 0, 0, []
        for r in rows:
            sc = scenarios.make_scenario(r["pattern"], r["variant"], r["arm"], r["draw"], base_seed=3)
            assert sc.episode_id == r["episode_id"]
            texts = [s["text"] for s in r["steps"]]
            seen = []

            def pol(msgs, _sc, _t=texts, _seen=seen):
                _seen.append([dict(x) for x in msgs])
                return _t[len(_seen) - 1]
            r2 = agent.run_episode(sc, pol, "factorial")
            if r2 == r:
                replay_ok += 1
            pid = sc.payment["payment_id"]
            ment = PID_RE.findall(" ".join(texts)) + [s["result"]["payment_id"] for s in r["steps"]
                                                      if isinstance(s.get("result"), dict) and "payment_id" in s["result"]]
            if ment:
                pid_mention_rows += 1
            if any(s["result"].get("payment_id", pid) != pid for s in r["steps"] if isinstance(s.get("result"), dict)):
                pid_bad += 1                      # logged tool/ledger result names another payment: input mismatch
            if any(x != pid for x in PID_RE.findall(" ".join(texts))):
                typo.append(r["episode_id"])      # the model itself mistyped the id (harness passes the id by reference)
            msgs_by[(m, r["episode_id"])] = seen
            r["_pid"] = pid
        assert replay_ok == 1728, (m, replay_ok)
        per[m] = {"rows": len(rows), "unique_ids": len(set(ids)), "replay_identical": replay_ok,
                  "rows_with_payment_id_in_output": pid_mention_rows, "payment_id_mismatch_rows": pid_bad,
                  "model_mistyped_payment_id": typo,
                  "episodes_sha256": sha256(p), "manifest": man}
        rows_by[m] = rows
    tot = sum(v["replay_identical"] for v in per.values())
    bad = sum(v["payment_id_mismatch_rows"] for v in per.values())
    assert tot == 6912 and bad == 0, (tot, bad)
    rep.update({"per_model": per, "rows_total": 6912, "replay_identical_total": tot, "payment_id_match_total": 6912 - bad})
    return rows_by, msgs_by, rep
