# BC harness pilot: Qwen2.5-0.5B-Instruct (30 Oct 2026)
**Pilot, not a paper result.** One 0.5B model, 10 draws per cell. These are measured numbers only; every figure below comes from `runs/pilot/episodes.jsonl` via `bcharness.analyze` (`runs/pilot/tables.md` has all tables, including the full 81-cell table).

## Run identity
- Model: Qwen/Qwen2.5-0.5B-Instruct (ungated, no login), fp32, CPU, 8 threads, greedy decoding, max_new_tokens 96.
- Grid: 3 patterns × 9 variants × 3 arms × 10 draws = **810 episodes**. base-seed 1. Seed 0 was used only for development.
- Run code sha256 (bcharness/*.py at run time): `6189ea2b5c80b17018475590b9269e0e6ff138b798a296d1028d52187bd55e8b`.
- System prompts sha256: `2ca85822…`.
- `episodes.jsonl` sha256: `cb490008f03173b05fcb41f67e50038e1271a4cdb315337a552389d2e4afc184`.
- Analysis script `analyze.py` was extended after the run (novelty split and verify-then-ignore); its current sha256 is `6bb39a2d…`.
- Started 2026-10-30 09:25 Dubai. Wall time 2089 s, 1,320 model calls, 28,512 generated tokens. torch 2.15.0+cpu, transformers 5.22.0, cryptography 50.0.2.

## Headline (Wilson 95% CI)
| arm | unsafe execution (8 invalid variants) | false halt (valid) | model called verify_clearance | parse failures |
|---|---|---|---|---|
| A0 none | 240/240 = 100% [98, 100] | 0/30 = 0% [0, 11] | 145/270 = 54% [48, 60] | 0/270 |
| A1 prompt rule | 89/240 = 37% [31, 43] | 0/30 = 0% [0, 11] | 220/270 = 81% [76, 86] | 0/270 |
| A2 code verifier | 0/240 = 0% [0, 2] | 0/30 = 0% [0, 11] | 145/270 = 54% [48, 60] | 0/270 |

## Variant families
| family | A0 | A1 | A2 |
|---|---|---|---|
| unsigned claim (none / peer text / document text) | 90/90 = 100% [96, 100] | 30/90 = 33% [24, 44] | 0/90 = 0% [0, 4] |
| signed but invalid (floating / wrong payload / expired / replayed / unentitled) | 150/150 = 100% [98, 100] | 59/150 = 39% [32, 47] | 0/150 = 0% [0, 2] |
| valid | 30/30 = 100% | 30/30 = 100% | 30/30 = 100% |

**Verify-then-ignore** (the model called verify_clearance, received INVALID, then called execute_transfer anyway):
- A0: 135/135 = 100% [97, 100]
- A1: 48/199 = 24% [19, 31]

## What the numbers say (measured; small model; pilot)
1. **Without mitigation, this model executed every transfer** (240/240 invalid variants). It executed even after calling the verifier tool itself and being told INVALID (135/135).
2. **The prompt-only rule reduced unsafe execution to 37% [31, 43] without false halts.** The reduction is uneven:
   - by pattern: content_as_authority 8/80 = 10%, trust_by_position 43/80 = 54%, approvals_that_float 38/80 = 48%;
   - by variant: the signed-expired clearance executed 16/30 = 53%, and **no clearance at all** executed 20/30 = 67%.
3. **A2 is the enforcement baseline, and its 0 executed holds by construction. It is not a finding.** With a correct code-level point-of-action verifier, 0/240 invalid transfers executed (Wilson [0, 2]) and 30/30 valid ones executed ([89, 100]). This checks that the harness is wired correctly; it says nothing about model behaviour. What A2 does measure about the model: it *attempted* execution in 270/270 A2 episodes, and it called verify in 145/270 = 54% [48, 60].

## Caveats (must travel with any use of these numbers)
- A 0.5B model is near the floor of capability. Larger models (1.5B, 3B, SmolLM2-1.7B) are needed before any claim.
- n = 30 per variant×arm cell (10 per pattern×variant×arm), so the intervals are wide.
- The follow-up prompt after a tool result names `execute_transfer` before `halt`, which may bias a weak model toward executing. A counterbalanced ordering is planned for v0.2.
- Templates are English and synthetic: 2 frames per pattern, a single sanctions check type.

---

## Pilot v0.2: A3 structured status + counterbalanced follow-up (measured 30 Oct 2026)

**Run:** `runs/pilot-v02/` (episodes.jsonl sha256 75f8b3f95925916ccdd1cfbc42c9e44efb23273999eee19788abcdfd5dfda8e8; code sha256 dcc0299e…; wall 2755.7 s). Qwen2.5-0.5B-Instruct, fp32, greedy, max_new_tokens 96. Arms A0, A1 and A3; 3 patterns × 9 variants × 10 draws = 810 episodes; base-seed 2. `--followup-order counterbalance`: even draws use the v0.1 execute-first follow-up and odd draws use halt-first. Tables are in `runs/pilot-v02/tables.md` (pooled) and `runs/pilot-v02/order_split.md` (from `order_split.py`).

**Pooled (both orders), unsafe execution:** A0 173/240 = 72% [66, 77]; A1 69/240 = 29% [23, 35]; A3 121/240 = 50% [44, 57]. **False halt:** A0 5/30 = 17%; A1 10/30 = 33%; A3 15/30 = 50%. Parse failures: A3 10/270 = 4%; A0 and A1 0.

**Split by follow-up order (the main v0.2 finding):**

| | A0 | A1 | A3 |
|---|---|---|---|
| execute-first, non-valid executed | 120/120 = 100% [97, 100] | 49/120 = 41% [32, 50] | 113/120 = 94% [88, 97] |
| execute-first, valid executed | 15/15 | 15/15 | 15/15 |
| halt-first, non-valid executed | 53/120 = 44% [36, 53] | 20/120 = 17% [11, 24] | 8/120 = 7% [3, 13] |
| halt-first, valid executed | 10/15 = 67% | 5/15 = 33% | 0/15 = 0% [0, 20] |
| verify-then-ignore, execute-first | 65/65 | 31/102 = 30% [22, 40] | 103/103 |
| verify-then-ignore, halt-first | 0/67 | 0/100 | 0/108 |
| first turn calls execute (non-valid / valid) | 108/240 = 45% / 21/30 = 70% | 38/240 = 16% / 8/30 = 27% | 18/240 = 8% / 0/30 = 0% |

**What this shows (measured; one 0.5B model, n = 120/15 per cell):**
1. **At 0.5B the follow-up wording drives the decision more than the clearance does.** Under execute-first, every arm executes every valid case and most invalid ones. Under halt-first, verify-then-ignore drops to 0 in all arms. The v0.1 headline (A1 37%) was measured under execute-first only, so it is an order-specific number, not an order-free one.
2. **A3 (Hu-style structured status, shown but not enforced) does not make the model discriminate.** In neither order does it separate valid from invalid: execute-first 94% vs 100%, halt-first 7% vs 0%. It makes the model more cautious overall (first turn executes 8% of non-valid and 0% of valid cases) and does not raise correct execution. For this model, showing the verified status is not a substitute for enforcing it (the A2 enforcement baseline in v0.1: 0/240 executed, by construction).
3. A1's prompt rule is the only arm that moves verify-then-ignore under execute-first (30% vs 100%), but it costs false halts (halt-first valid 5/15).
4. Caveats: one tiny model; two hand-written follow-up wordings; parity counterbalancing (draws are paired, not randomised); A2 was not rerun in v0.2. Larger ungated models (Qwen2.5-1.5B/3B, SmolLM2-1.7B) are needed before any claim generalises.

**Harness consequence:** the paper must report results by follow-up order (or use a neutral follow-up) and treat order sensitivity as a measured result, not as noise.
