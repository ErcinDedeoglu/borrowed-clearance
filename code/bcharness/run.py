"""Run the BC grid. Example:
  python -m bcharness.run --policy hf --model Qwen/Qwen2.5-0.5B-Instruct --draws 10 --out ../runs/pilot
  python -m bcharness.run --policy verify_then_follow --draws 2 --out /tmp/x
Writes episodes.jsonl (one line per episode) and manifest.json (config, code hash, versions, timing)."""
import argparse, hashlib, json, os, pathlib, platform, sys, time
from . import scenarios
from .agent import run_episode, SYSTEM, FOLLOWUP_ORDERS
from .policies import SCRIPTED, HFPolicy


def code_hash():
    root = pathlib.Path(__file__).parent
    h = hashlib.sha256()
    for f in sorted(root.glob("*.py")):
        h.update(f.name.encode()); h.update(f.read_bytes())
    return h.hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default="hf", choices=["hf"] + list(SCRIPTED))
    ap.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct")
    ap.add_argument("--dtype", default="fp32", choices=["fp32", "bf16"])
    ap.add_argument("--draws", type=int, default=2)
    ap.add_argument("--base-seed", type=int, default=0)
    ap.add_argument("--max-new-tokens", type=int, default=96)
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--arms", default=",".join(scenarios.ARMS),
                    help="comma list from " + ",".join(scenarios.ALL_ARMS) + " (default: the v0.1 arms A0-A2)")
    ap.add_argument("--followup-order", default="execute_first", choices=FOLLOWUP_ORDERS)
    ap.add_argument("--out", required=True)
    ap.add_argument("--resume", action="store_true",
                    help="checkpoint/resume: keep complete lines already in episodes.jsonl and skip those episode_ids")
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    policy = HFPolicy(a.model, a.dtype, a.max_new_tokens, a.threads) if a.policy == "hf" else SCRIPTED[a.policy]
    load_s = time.time() - t0
    n = 0
    path = os.path.join(a.out, "episodes.jsonl")
    done = set()
    if a.resume and os.path.exists(path):
        good = []
        for line in open(path):
            try:
                r = json.loads(line); done.add(r["episode_id"]); good.append(line if line.endswith("\n") else line + "\n")
            except (json.JSONDecodeError, KeyError):
                pass   # a torn last line from a crash is dropped and rerun
        open(path, "w").writelines(good)
    resumed = len(done)
    with open(path, "a" if a.resume else "w") as f:
        arms = tuple(x.strip() for x in a.arms.split(",") if x.strip())
        assert all(x in scenarios.ALL_ARMS for x in arms), arms
        for sc in scenarios.grid(a.draws, a.base_seed, arms=arms):
            if sc.episode_id in done:
                continue
            r = run_episode(sc, policy, a.followup_order)
            f.write(json.dumps(r) + "\n"); f.flush()
            n += 1
            if n % 27 == 0:
                print(f"{n} episodes, {time.time() - t0:.0f}s", flush=True)
    import importlib.metadata as md
    vers = {}
    for p in ("torch", "transformers", "cryptography"):
        try: vers[p] = md.version(p)
        except md.PackageNotFoundError: pass
    man = {"policy": a.policy, "model": a.model if a.policy == "hf" else None, "dtype": a.dtype if a.policy == "hf" else None,
           "decoding": "greedy (do_sample=False)" if a.policy == "hf" else "scripted", "max_new_tokens": a.max_new_tokens,
           "draws": a.draws, "base_seed": a.base_seed, "episodes": n + resumed, "episodes_this_process": n, "resumed_from": resumed, "arms": list(arms), "followup_order": a.followup_order,
           "grid": {"patterns": scenarios.PATTERNS, "variants": scenarios.VARIANTS, "arms": list(arms)},
           "code_sha256": code_hash(), "system_prompts_sha256": hashlib.sha256(json.dumps(SYSTEM, sort_keys=True).encode()).hexdigest(),
           "python": platform.python_version(), "versions": vers, "load_seconds": round(load_s, 1),
           "wall_seconds": round(time.time() - t0, 1),
           "wordings": __import__("bcharness.agent", fromlist=["WORDINGS"]).WORDINGS if a.followup_order == "factorial" else None,
           "started": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(t0))}
    if a.policy == "hf":
        man.update({"model_calls": policy.calls, "gen_seconds": round(policy.gen_seconds, 1), "new_tokens": policy.new_tokens})
    json.dump(man, open(os.path.join(a.out, "manifest.json"), "w"), indent=1)
    print(json.dumps({k: man[k] for k in ("episodes", "wall_seconds", "code_sha256")}))


if __name__ == "__main__":
    main()
