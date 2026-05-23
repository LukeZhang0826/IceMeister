# backend

Cloud / server-side services. Candidate responsibilities:

- Telemetry ingest and storage
- Fleet management (if more than one unit)
- OTA firmware delivery
- Remote control / monitoring API for the frontend

**Status:** placeholder. Language and framework not yet chosen.

**Likely candidates:**
- Node + Fastify / Hono (would join the pnpm workspace)
- Python + FastAPI
- Go + standard library / chi
- Rust + Axum

Will define its own deployment target separately from the static frontend.
