#!/bin/bash
# Resume of SmolLM2-1.7B-Instruct after 3 global-OOM kills (rc=137). Identical command/flags to run_all.sh; only
# engineering change is machine-level: an 8 GB swapfile (/swapfile-bcrun) added 31 Oct 2026 ~07:36 Dubai. Reported as deviation D1 in the paper (Appendix D) and the pre-registration.
cd "$(dirname "$0")/../../code"   # release: was an absolute path on the build machine
PY=${PY:-python3}   # release: was ../../.venv/bin/python
OUT=../runs/main
spec="HuggingFaceTB/SmolLM2-1.7B-Instruct fp32"
set -- $spec; tag=$(basename $1)
for attempt in 4 5 6; do
  echo "BEGIN $tag attempt $attempt $(date '+%F %T %z')" >> $OUT/progress.log
  nice -n 19 $PY -m bcharness.run --policy hf --model $1 --dtype $2 --threads 6 --draws 16 --base-seed 3 \
    --arms A0_none,A1_prompt_rule,A2_code_verifier,A3_structured_status --followup-order factorial --resume \
    --out $OUT/$tag >> $OUT/$tag.log 2>&1
  rc=$?; echo "END $tag attempt $attempt rc=$rc rows=$(wc -l < $OUT/$tag/episodes.jsonl 2>/dev/null) $(date '+%F %T %z')" >> $OUT/progress.log
  [ $rc -eq 0 ] && break
  sleep 120   # let box memory pressure ease before retrying
done
echo "ALL_DONE $(date '+%F %T %z')" >> $OUT/progress.log
