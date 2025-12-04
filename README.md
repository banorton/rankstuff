# RankStuff

Ranked voting polls using Borda count.

## Running Locally

```bash
cd api
cp .env.example .env  # configure MongoDB URL and JWT secret
uv run uvicorn main:app --reload
```

API docs: http://localhost:8000/docs
