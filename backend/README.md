# backend

IceMeister's telemetry service. Runs off the vehicle and is the only thing the frontend talks to.

**Status:** placeholder.

**Stack:** Kotlin. Framework not yet chosen.

**Architecture:** starting as a single monolith service. Split it apart only if a specific part needs to scale or deploy independently.

Responsibilities:

- Ingest telemetry from the onboard controller and store it
- Serve telemetry and vehicle status to the frontend
- Fleet management, once there is more than one unit
- OTA update delivery, later

The backend is never part of the vehicle's safety path. The vehicle has to stay safe if the backend or the network goes down.

Not part of the pnpm workspace. Will define its own build and deployment target separately from the static frontend.
