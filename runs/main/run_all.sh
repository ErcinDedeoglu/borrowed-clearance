#!/bin/bash
# v0.3 main experiment, pre-registered in ../../prereg-2026-10-30.md. Sequential models, nice 19, 6 threads, resumable.
# Re-running this script resumes where it stopped (bcharness.run --resume skips finished episode_ids).
cd "$(dirname "$0")/../../code"   # release: was an absolute path on the build machine
PY=${PY:-python3}   # release: was ../../.venv/bin/python
OUT=../runs/main
while pgrep -f smoke-dev/smoke.sh >/dev/null; do sleep 30; done      # do not share CPU/RAM with the dev smoke test
echo "START $(date '+%F %T %z')" >> $OUT/progress.log
for spec in "Qwen/Qwen2.5-0.5B-Instruct fp32" "Qwen/Qwen2.5-1.5B-Instruct fp32" \
            "HuggingFaceTB/SmolLM2-1.7B-Instruct fp32" "Qwen/Qwen2.5-3B-Instruct bf16"; do
  set -- $spec; tag=$(basename $1)
  for attempt in 1 2 3; do
    echo "BEGIN $tag attempt $attempt $(date '+%F %T %z')" >> $OUT/progress.log
    nice -n 19 $PY -m bcharness.run --policy hf --model $1 --dtype $2 --threads 6 --draws 16 --base-seed 3 \
      --arms A0_none,A1_prompt_rule,A2_code_verifier,A3_structured_status --followup-order factorial --resume \
      --out $OUT/$tag >> $OUT/$tag.log 2>&1
    rc=$?; echo "END $tag attempt $attempt rc=$rc rows=$(wc -l < $OUT/$tag/episodes.jsonl 2>/dev/null) $(date '+%F %T %z')" >> $OUT/progress.log
    [ $rc -eq 0 ] && break
  done
done
echo "ALL_DONE $(date '+%F %T %z')" >> $OUT/progress.log
