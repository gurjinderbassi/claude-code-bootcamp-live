# notes-api-smoke — invocation record

**Skill:** `module-09/notes-api-smoke/SKILL.md`  
**Target:** `module-09/main.py`  
**Port:** 8099  
**Runner:** `python3 -m uvicorn module-09.main:app` (uv not installed; fastapi + uvicorn present in system Python 3.12)  
**Date:** 2026-05-30

## Output

```
[PASS] POST /notes → 201
[PASS] GET /notes → 200
[PASS] GET /notes/1 → 200
[PASS] PATCH /notes/1 → 200
[PASS] DELETE /notes/1 → 204
[PASS] GET /notes/999 → 404
6/6 checks passed.
```

## Server log

```
INFO:     Started server process [83678]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8099 (Press CTRL+C to quit)
INFO:     127.0.0.1:64333 - "GET /notes HTTP/1.1" 200 OK
INFO:     127.0.0.1:64334 - "POST /notes HTTP/1.1" 201 Created
INFO:     127.0.0.1:64335 - "GET /notes HTTP/1.1" 200 OK
INFO:     127.0.0.1:64336 - "GET /notes/1 HTTP/1.1" 200 OK
INFO:     127.0.0.1:64337 - "PATCH /notes/1 HTTP/1.1" 200 OK
INFO:     127.0.0.1:64338 - "DELETE /notes/1 HTTP/1.1" 204 No Content
INFO:     127.0.0.1:64339 - "GET /notes/999 HTTP/1.1" 404 Not Found
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [83678]
```
