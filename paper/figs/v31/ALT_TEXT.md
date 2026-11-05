# Alt text for the v3.1 figures (one line each; numbers are in the captions and CSVs)

- fig_threat: Diagram. An authorized payment executor receives evidence that a sanctions screen cleared the payment through one of three relay channels, each writable by a different party; a bottom box marks where a code check can sit.
- fig_harness_v31: Flow diagram of one episode. Issuer, clearance variant and channel feed the acting payment agent, which is set by one of four arms and can call verify, execute or halt; the verifier and, in arm A2 only, a code gate sit in front of a mock ledger; a deterministic scorer reads the ledger and the tool calls.
- fig_design_v31: Grid of three channels by nine clearance variants, every cell holding 16 draws, grouped into unsigned claims, signed-but-invalid clearances and the valid clearance, with the list of eight follow-up conditions on the right.
- fig_traj_schematic: Schematic of four rows, one per arm, for the same synthetic payment: A0 verifies, gets INVALID and executes (ledger executed); A1 verifies, gets INVALID and halts; A2 verifies, gets INVALID, calls execute and is blocked by the code gate; A3 sees a status line reading INVALID (no_clearance) and executes (ledger executed).
- fig_traj_full: Four side-by-side tool-call sequences for the same synthetic payment, one per arm, with the verbatim model outputs and tool results of each turn.
- fig_main_arm: Four bar-chart panels, one per model, of the executed percentage for non-valid and valid clearances under the four arms, with Wilson intervals.
- fig_main_wording: Four stacked bar-chart panels, one per model, of unsafe execution for each of eight follow-up conditions under the four arms.
- fig_dumbbell: Dumbbell plot per model comparing unsafe execution when execute is named first versus halt first, for wordings W1 to W3 and each arm, with the neutral wordings below a dotted line.
- fig_main_variant: Four stacked bar-chart panels, one per model, of the executed percentage for each of nine clearance variants under the four arms.
- fig_heat: Grid of heatmaps, models by arms, giving executed counts out of 16 for every channel and clearance-variant cell, on one shared colour scale.
- fig_flow: Stacked horizontal bars splitting the non-valid episodes of each model and arm into six trajectory types, from first-turn execution to unparsed output.
- fig_vti: Bar chart of the share of episodes that executed after the agent's own verifier returned INVALID, by returned reason, for two models and three arms.
- fig_frontier: Four scatter panels, one per model, of safety (non-valid clearances not executed) against utility (valid clearances executed), one marker per arm with Wilson intervals. Markers are shifted horizontally for display by at most 1.5 percentage points so that coinciding arms stay visible; in the Qwen2.5-1.5B and Qwen2.5-3B panels several arms sit at or near the same corner.
- fig_pilot: Two bar-chart panels for the pilot runs: executed percentage by clearance variant (pilot v0.1) and by follow-up order (pilot v0.2).
