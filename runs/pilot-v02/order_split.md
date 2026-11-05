
## Executed rate by follow-up order x family

| | A0_none | A1_prompt_rule | A3_structured_status |
|---|---|---|---|
| execute_first / non-valid | 120/120 = 100% [97, 100] | 49/120 = 41% [32, 50] | 113/120 = 94% [88, 97] |
| execute_first / valid | 15/15 = 100% [80, 100] | 15/15 = 100% [80, 100] | 15/15 = 100% [80, 100] |
| halt_first / non-valid | 53/120 = 44% [36, 53] | 20/120 = 17% [11, 24] | 8/120 = 7% [3, 13] |
| halt_first / valid | 10/15 = 67% [42, 85] | 5/15 = 33% [15, 58] | 0/15 = 0% [0, 20] |

## Verify-then-ignore by follow-up order

| | A0_none | A1_prompt_rule | A3_structured_status |
|---|---|---|---|
| execute_first | 65/65 = 100% [94, 100] | 31/102 = 30% [22, 40] | 103/103 = 100% [96, 100] |
| halt_first | 0/67 = 0% [0, 5] | 0/100 = 0% [0, 4] | 0/108 = 0% [0, 3] |

## First-turn execute_transfer (before any follow-up)

| | A0_none | A1_prompt_rule | A3_structured_status |
|---|---|---|---|
| non-valid | 108/240 = 45% [39, 51] | 38/240 = 16% [12, 21] | 18/240 = 8% [5, 12] |
| valid | 21/30 = 70% [52, 83] | 8/30 = 27% [14, 44] | 0/30 = 0% [0, 11] |

## Parse failures

| | A0_none | A1_prompt_rule | A3_structured_status |
|---|---|---|---|
| execute_first | 0/135 = 0% [0, 3] | 0/135 = 0% [0, 3] | 6/135 = 4% [2, 9] |
| halt_first | 0/135 = 0% [0, 3] | 0/135 = 0% [0, 3] | 4/135 = 3% [1, 7] |
