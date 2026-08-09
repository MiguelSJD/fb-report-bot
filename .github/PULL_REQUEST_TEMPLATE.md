## Summary
<!-- Briefly explain the core objective of this PR and what problem it solves -->

---

## Key Changes
<!-- Provide a breakdown of what was modified, added, or removed. Group by system/component (e.g., Configuration, Database, Commands) where helpful. -->

---

## How to Test

### 1. Local Stack Environment Setup
Copy `.env.example` to `.env` and fill in your secrets, ensuring `credentials.json` is placed in the project root:

```bash
cp .env.example .env
```

### 2. Deploy Containerized Stack
```bash
docker compose up -d --build
```

### 3. Verify Execution & Logs
```bash
docker compose logs -f
```