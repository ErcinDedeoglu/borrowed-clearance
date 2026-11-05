#!/bin/bash
# Dev-seed (0) timing smoke test, excluded from all analysis. Only timing and parse failures are inspected.
cd "$(dirname "$0")/../../code"   # release: was an absolute path on the build machine
PY=${PY:-python3}   # release: was ../../.venv/bin/python
for spec in "Qwen/Qwen2.5-1.5B-Instruct fp32" "HuggingFaceTB/SmolLM2-1.7B-Instruct fp32" "Qwen/Qwen2.5-3B-Instruct bf16"; do
  set -- $spec; tag=$(basename $1)
  nice -n 19 $PY -m bcharness.run --policy hf --model $1 --dtype $2 --threads 6 --draws 1 --base-seed 0 \
     --arms A3_structured_status --followup-order factorial --out ../runs/smoke-dev/$tag > ../runs/smoke-dev/$tag.log 2>&1
done
echo SMOKE_DONE
