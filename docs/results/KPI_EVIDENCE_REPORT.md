# BizPilot AI — KPI Evidence Report

Generated: 2026-10-09T16:53:20.765461+00:00
Git branch: feature/analytics-testing
Git commit: 0194b98394da174e80f7146552e9aaee8f9a1517

## KPI Summary

| KPI | Target | Actual | Status |
|---|---|---|---|
| Intent Accuracy | >=95% | Not measured | NOT TESTED |
| UI Accuracy | >=95% | Not measured | NOT TESTED |
| Task Success | >=90% | Not measured | NOT TESTED |
| Analytical Accuracy | <=1% error | Not measured | NOT TESTED |
| Explanation Faithfulness | >=95% | Not measured | NOT TESTED |
| Retrieval Quality | Recall@3 >=95% | 96.00% | PARTIAL |
| Safety and Reliability | Zero unauthorized actions | Not measured | NOT TESTED |
| Performance and UX | Measure p50/p95 | Not measured | NOT TESTED |

## Retrieval Evaluation

Results below are from the offline metadata benchmark.
They do not establish end-to-end agent task success.

| Method | P@1 | Recall@3 | MRR | p50 ms | p95 ms |
|---|---:|---:|---:|---:|---:|
| tfidf | 42.00% | 66.00% | 54.85% | 0.203 | 0.290 |
| faiss | 78.00% | 96.00% | 86.62% | 10.507 | 12.354 |
| hybrid | 46.00% | 86.00% | 66.59% | 10.746 | 12.636 |

## Dataset Audit

Status: PASS
Issues found: 0

## Evidence

- `evaluation/results/advanced/comparison.json`
- `evaluation/results/dataset_audit_report.json`
- `data/benchmarks/advanced_retrieval_ground_truth.jsonl`

## Limitations

- Retrieval results are from an offline metadata benchmark.
- The advanced benchmark may contain generated or template-derived queries.
- End-to-end agent actions and UI state are not yet verified here.
- Retrieval latency excludes model loading and index construction.
- Agent response latency must be measured separately.

## Next Actions

1. Validate the dataset audit and resolve any issues.
2. Review the advanced benchmark labels independently.
3. Connect the agent to the application and backend APIs.
4. Run authenticated end-to-end task tests.
5. Measure all eight KPIs on the deployed application.