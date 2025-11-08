# cc-sdd Mapping — orchestrator-service

## Task → Requirement IDs
- 0. Bootstrap orchestrator package → 1.1
- 1. Core data models (TaskStatus, SubTask, Decomposition, RoutingDecision, TaskResult, SynthesizedResponse, OrchestratorTask, ConstraintModel) → 1.1, 2.2–2.5, 3.5, 4.5, 5.5, 6.1, 6.5, 8.2, 8.4
- 2.1 ConstraintModelLoader (load/combine/reload/extract rules/threshold) → 1.1–1.5, 5.4
- 3.1 TaskDecomposer (prompting, parsing, confidence) → 2.1–2.5, 5.1
- 4.1 TaskRouter (candidate/query/filter/apply rules/select/confidence) → 3.1–3.5, 5.2, 10.3
- 5.1 ExecutionCoordinator (execute, retry, fallback, sync/async, ids, status, spores, provenance) → 2.4, 3.5, 6.2–6.4, 7.1–7.4, 8.1–8.5, 10.1, 10.4, 10.5
- 6.1 ResultSynthesizer (combine/conflicts/provenance/partial/confidence) → 4.1–4.5, 5.3, 6.5, 7.5
- 7.1 ConfidenceEvaluator (decomposition, routing, synthesis, threshold, escalate) → 5.1–5.5
- 8.1 MetricsTracker (decomposition, routing, synthesis, confidence, errors) → 9.1–9.5
- 9.1 OrchestratorService API (process pipeline, status, cancel, reload, metrics) → 1.5, 5.5, 8.1–8.5, 9.1
- 10.1 FastAPI endpoints (task submit/status/cancel/reload/metrics) → 1.5, 8.1–8.5, 9.1
- 11.1 MCP integration (service discovery, context exchange, tools, trace) → 3.5, 6.2, 10.1–10.5
- 12.1 Example constraint models (TTL/JSON/MD with routing and thresholds) → 1.1–1.4
- 13.1 Error handling/logging (service unavailable/failure/decomposition/synthesis) → 7.1–7.5
- 14.x Unit tests (loader/decomposer/router/executor/synthesizer/confidence/metrics) → section-wise coverage above
- 15.x Integration tests (mock services, E2E, MCP flows, errors) → 10.1–10.5 and cross-cutting 2–9
- 16.x Dependencies/config (Redis, env vars) → 1.1, 5.4, 7.1, 8.1, 8.2
- 17.x Documentation (API + constraint formats) → All (overview and user guidance)


