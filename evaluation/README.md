
# BizPilot AI Agent Evaluation Contract

## Input
data/benchmarks/intent_benchmark.jsonl

## Agent output
evaluation/results/agent_predictions.jsonl

Each output record must contain:
- test_id
- predicted_intent
- predicted_page_id
- actual_ui_state
- executed_actions
- retrieved_metadata_ids
- latency_ms
- task_completed
- verified
- unsupported_action_attempts

## Rules
1. Predictions must come from actual agent execution.
2. UI state must be read back from the application.
3. Tool actions must be logged.
4. Completion must be verified independently.
5. Never mark a failed action as successful.
6. Include test failures and timeouts in the report.
7. Do not train or tune using the held-out test set.
