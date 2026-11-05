# Borrowed Clearance: harness, pre-registration and run records

Code and synthetic data for "Borrowed Clearance: Do LLM Payment Agents in Banking Act on Invalid Compliance Clearances?" (Ercin Dedeoglu, ORCID 0009-0004-0792-5310).

- `code/`: the `bcharness` package, tests and the exact dependency lock. Start with `code/README.md`.
- `prereg-2026-10-30.md`: the pre-registration exactly as frozen on 30 Oct 2026 at 11:01 Asia/Dubai (UTC+4), before the main runs. Its sha256 is in `PREREG-SHA256.txt`. Deviations from it are reported in the paper (Appendix D).
- `runs/`: run scripts, manifests (code hash, seeds, library versions) and per-episode logs (`episodes.jsonl`).
- `paper/figs/`: figure and table scripts and the files they produce. `make_figs.py` and `make_tab_percond.py` build the earlier figures and tables; the `*_v31.py` scripts, with `stats_v3.py` and `v3_integrity.py`, build the figures, tables and exhibits into `paper/figs/v31/`. The current paper is v3.3.1. `widen_v32.py` redraws 3 TikZ diagrams at the full text width of 6.5in. It changes only horizontal spacing and writes the diagrams to `tikz/v32/` and `v32/`. `make_positioning_v32b.py` writes the related-work comparison table and its per-cell evidence (`positioning_v32b.json`) into `v32b/`. `make_manifest_v32b.py` writes `v32b/MANIFEST.json` for paper v3.2b. For v3.3, `make_positioning_v33.py` and `make_tabs_v33.py` rewrite the related-work comparison table and the paired-tests table into `v33/` with the same rows and the v3.3 legend and heading (the legend text is in `v33/tab_positioning_legend.tex`), and `manifest_v33.py` writes `v33/MANIFEST.json` and the provenance table `v33/tab_provenance.tex` for paper v3.3. For the current paper, v3.3.1, `manifest_v331.py` writes `v331/MANIFEST.json` (`v33/MANIFEST.json` with `manifest_v331.py` added to the scripts) and the provenance table `v331/tab_provenance.tex`, whose input key X names `make_exhibits_v31.py`. `make_exhibits_v3.py` and `tikz/fig_traj.tex` are kept because the v3.1 build reads the TikZ wrapper and the manifest records the script.

## Rebuilding the current figures and tables

From `paper/figs/`, in this order:

1. `python stats_v3.py` and `python make_exhibits_v31.py` (harness environment, `code/requirements-lock.txt`). Both first replay every main-run episode through the unchanged harness and stop if any logged record does not match.
2. `python make_figs_v31.py`, `python redraw_v31.py` and `python make_tabs_v31.py` (`requirements-figs-v3.txt`; the TikZ figures need `tectonic` on PATH or `TECTONIC=/path/to/tectonic`).
3. `python strip_meta.py v31/*.pdf`, then `python manifest_v31.py` to write `v31/MANIFEST.json` (sha256 of every script, input and output) and `v31/tab_provenance.tex`. `python check_figs.py --width-in 6.5 v31/fig_main_arm.pdf` checks fonts and printed width.
4. `python widen_v32.py` (needs `tectonic`, as in step 2), `python strip_meta.py v32/*.pdf`, `python make_positioning_v32b.py` and `python make_manifest_v32b.py`.
5. `python make_positioning_v33.py`, `python make_tabs_v33.py` and `python manifest_v33.py`.
6. `python manifest_v331.py`.

All CSV, JSON and table files rebuild byte-identically, apart from the `MANIFEST.json` files and the provenance tables `v31/tab_provenance.tex`, `v33/tab_provenance.tex` and `v331/tab_provenance.tex`, which record the PDF hashes. The paper's related-work comparison table is a literature record, not a run output. Its evidence record is `v32b/positioning_v32b.json` (each cell read from the cited paper; also shipped with the arXiv source as `anc/positioning_v32b.json`). `make_positioning_v32b.py` built that record from the earlier v3.1 record, `v31/positioning_v31.json`, which is held internally and not included here. Without it, the script reads `v32b/positioning_v32b.json` and `v32b/tab_positioning_notes.tex` (the table's notes) and rebuilds `v32b/tab_positioning.tex` byte for byte. `v31/MANIFEST.json` and `v31/tab_provenance.tex` omit the table and its input; `v32b/MANIFEST.json`, `v33/MANIFEST.json` and `v331/MANIFEST.json` record it. The paper's copy of each table in `v33/` is that file without its first (comment) line. The provenance table printed in paper v3.3.1 is `v331/tab_provenance.tex` without its first (comment) line. The eight TikZ PDFs (five in `v31/`, three in `v32/`) rebuild with identical text and page size; their bytes can differ between builds.

All data are synthetic. Licence: Apache-2.0 (see `LICENSE` and `NOTICE`).
