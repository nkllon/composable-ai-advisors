# cc-sdd Mapping — domain-model-framework

## Task → Requirement IDs
- 1. Set up domain model framework structure → All
- 2. Update backend dependencies → 2.4, 3.3, 4.4
- 3.1 Models (enums, metadata, model, validation result, exceptions) → 1.1, 1.2, 1.3, 3.4, 4.5, 9.4
- 4.1 ModelLoader (base dir, UTF-8, detect/resolve, concurrent) → 2.1, 2.2, 2.3, 2.4, 2.5
- 4.2 Loader error handling → 1.5, 2.3
- 4.3 Loader tests → 2.1, 2.2, 2.3, 2.4, 2.5
- 5.1 ModelParser (unified) → 3.1, 3.2, 3.3
- 5.2 Turtle parsing + metadata/capabilities → 1.1, 3.1, 3.4, 8.1–8.5
- 5.3 JSON parsing + metadata/capabilities → 1.2, 3.2, 3.4, 8.1–8.5
- 5.4 Markdown parsing + metadata/capabilities → 1.3, 3.3, 3.4, 8.1–8.5
- 5.5 Parsing error handling → 3.5
- 5.6 Parser tests → 3.1, 3.2, 3.3, 3.4, 3.5
- 6.1 ModelValidator (init/validate) → 4.1, 4.2, 9.1, 9.4
- 6.2 Format-specific validation → 4.3, 4.4
- 6.3 Validation error reporting → 4.5
- 6.4 Validator tests → 4.1–4.5, 9.1, 9.4
- 7.1 ModelRegistry (register/get/list/search/versions/unregister/index) → 5.1–5.5, 9.2, 9.3
- 7.2 Version tracking → 9.2, 9.3, 9.5
- 7.3 Registry tests → 5.1–5.5, 9.2, 9.3
- 8.1 ModelCache (TTL/stats/ops) → 6.1–6.5
- 8.2 Thread safety → 6.1–6.4
- 8.3 Cache tests → 6.1–6.5
- 9.1 Framework interface (load/get/cache/metrics/…)* → 5.3, 5.4, 5.5, 7.1–7.5, 9.3, 9.5, 10.4, 10.5
- 9.2 Logging & metrics → 10.1, 10.2, 10.3, 10.4
- 9.3 Framework tests → 7.1–7.5, 9.3, 9.5, 10.1–10.5
- 10.1 Fixtures (valid/invalid across formats) → All
- 11.1 Integration tests (E2E, reload, concurrency, cache) → All
- 12.1 Developer guide (formats/examples/metadata/rules) → All
- 12.2 API documentation (public methods/usage) → All

* includes pending items for reload, list/search, versions


