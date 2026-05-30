# Notes API

SQLite-backed REST API built with FastAPI + Pydantic v2.

## Run

```
uvicorn main:app --reload
```

Endpoints: `POST /notes`, `GET /notes?q=<query>`, `GET /notes/{id}`, `PATCH /notes/{id}`, `DELETE /notes/{id}`
