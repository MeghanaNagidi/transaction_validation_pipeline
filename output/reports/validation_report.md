# Validation report

Curated: **180 transactions**, **464 legs**; quarantined rows: **108**.

## Reconciliation checks (0 violations = pass)

| check | violations | result |
|---|---|---|
| curated_txns_balanced | 0 | PASS |
| total_debits_equal_total_credits | 0 | PASS |
| net_movement_sums_to_zero | 0 | PASS |
| no_orphan_accounts | 0 | PASS |
| no_currency_mismatch_vs_account | 0 | PASS |
| fact_txn_leg_count_matches_legs | 0 | PASS |
| fact_txn_total_matches_debits | 0 | PASS |
| no_txn_without_legs | 0 | PASS |
| run_counts_reconcile (read = accepted + rejected) | 0 | PASS |
| run_counts_reconcile (accepted = inserted + already_loaded) | 0 | PASS |
| rejects_traceable_to_run_and_source | 0 | PASS |
| curated_legs_equal_sum_of_inserted_rows | 0 | PASS |

## Pipeline runs

| run_id | source | status | read | accepted | inserted | already_loaded | rejected | txns_ok | txns_rejected | late | out_of_order | secs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| run_sample_001 | transactions.csv | SUCCESS | 389 | 335 | 335 | 0 | 54 | 130 | 20 | 3 | 25 | 0.0197 |
| run_sample_002_rerun | transactions.csv | SUCCESS | 389 | 335 | 0 | 335 | 54 | 130 | 20 | 3 | 25 | 0.0103 |
| run_20261105T041642_e6c6ac | transactions.csv | SUCCESS | 389 | 335 | 0 | 335 | 54 | 130 | 20 | 3 | 25 | 0.0415 |
| run_20261105T041754_de1e21 | transactions.csv | SUCCESS | 389 | 335 | 0 | 335 | 54 | 130 | 20 | 3 | 25 | 0.0285 |
| run_20261105T092514_4f7a0b | transactions.csv | SUCCESS | 518 | 464 | 129 | 335 | 54 | 180 | 20 | 3 | 55 | 0.0743 |
| run_20261105T101300_edd5cd | transactions.csv | SUCCESS | 518 | 464 | 0 | 464 | 54 | 180 | 20 | 3 | 55 | 0.0331 |
| run_20261106T094420_ca5c2d | transactions.csv | SUCCESS | 389 | 335 | 0 | 335 | 54 | 130 | 20 | 3 | 25 | 0.08 |
| run_20261106T095057_c7aba3 | transactions.csv | SUCCESS | 389 | 335 | 0 | 335 | 54 | 130 | 20 | 3 | 25 | 0.0736 |
| run_20261106T101938_297cf7 | transactions.csv | SUCCESS | 389 | 335 | 0 | 335 | 54 | 130 | 20 | 3 | 25 | 0.0773 |

## Rejects by reason

| reason_code | rows |
|---|---|
| TXN_REJECTED_PEER_LEG | 54 |
| INVALID_AMOUNT | 10 |
| DUPLICATE_CONFLICT | 8 |
| TXN_LEG_TS_SKEW | 6 |
| TXN_IMBALANCE | 6 |
| MISSING_REQUIRED_FIELD | 4 |
| MALFORMED_ROW | 4 |
| INGESTED_BEFORE_EVENT | 4 |
| CURRENCY_MISMATCH | 4 |
| ACCOUNT_CLOSED | 4 |
| UNKNOWN_ACCOUNT | 2 |
| DUPLICATE_LEG | 2 |

## Sample query: daily volume (first 7 days, minor units)

| date | txns | total_amount_minor |
|---|---|---|
| 2026-01-01 | 3 | 677433 |
| 2026-01-02 | 8 | 303000869917 |
| 2026-01-03 | 5 | 1523686 |
| 2026-01-04 | 8 | 100001657575 |
| 2026-01-05 | 7 | 101001182171 |
| 2026-01-06 | 7 | 201000944724 |
| 2026-01-07 | 3 | 200000290772 |

## Sample query: top 5 closing balances

| account_id | currency | closing_balance_minor |
|---|---|---|
| acc_00031 | JPY | 201029132272 |
| acc_00035 | JPY | 201001391139 |
| acc_00022 | INR | 200080985696 |
| acc_00012 | USD | 200073323774 |
| acc_00001 | EUR | 200015643054 |
