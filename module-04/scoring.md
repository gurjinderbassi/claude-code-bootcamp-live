# Scoring

| Criterion (0–3)  | Candidate A                                              | Candidate B                                                     |
|------------------|----------------------------------------------------------|-----------------------------------------------------------------|
| Correctness      | 3 — all 7 curls pass                                     | 2 — curl 5 (PATCH) returns 405; route is PUT, not PATCH        |
| Simplicity       | 3 — one clean file; context-manager DB pattern; modern lifespan handler | 2 — single file but verbose: manual conn open/close every handler, deprecated `@app.on_event`, extra `if __name__` block |
| Fit              | 2 — follows one-file convention and snake_case; timestamp deviates from CLAUDE.md format | 1 — deprecated startup hook emits a warning; PATCH→PUT breaks the spec; timestamp includes noisy microseconds |
| **Total**        | **8 / 9**                                                | **5 / 9**                                                       |

## Winner: Candidate A

Candidate A is the clear winner on correctness alone — it passes all seven smoke-test requests while candidate B returns 405 on the required `PATCH /notes/{id}` endpoint because it registered the route as `PUT` instead. Beyond correctness, candidate A is also simpler: it uses Python context managers for every database connection (no manual `conn.close()` calls), the modern FastAPI `lifespan` event handler instead of the deprecated `@app.on_event("startup")`, and adds title-validation logic that candidate B skips entirely. The only minor fit gap for candidate A is a timestamp format (`"%Y-%m-%dT%H:%M:%SZ"`) that differs slightly from the `"%Y-%m-%d %H:%M:%S UTC"` convention in CLAUDE.md, but that is a cosmetic deviation shared by both candidates and does not affect functionality.
