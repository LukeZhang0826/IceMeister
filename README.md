# IceMeister

Autonomous small zamboni. Built for community rinks, training facilities, and backyard installations the big machines can't reach.

> Specs, copy, and the 3D model on the landing page are placeholder while the hardware is in design.

**Live site:** https://icemeister.ca/

---

## Architecture

The system is split into layers, each running on its own hardware:

```
frontend (SPA, browser)
    |  HTTP
backend (Kotlin telemetry service, cloud)
    |  network
controller (onboard Linux computer, ROS 2)
    |  serial / CAN
firmware: main microcontroller (FreeRTOS, C++)
    |  serial / CAN / SPI / I2C
firmware: peripheral chips (bare-metal C)
```

- **Frontend** is a single-page app. It only ever talks to the backend, never to the vehicle directly.
- **Backend** is a Kotlin telemetry service, starting as a monolith. It sits off the vehicle.
- **Controller** is the onboard Linux computer running ROS 2. It handles autonomy (perception, localization, path planning) and relays telemetry to the backend.
- **Firmware** covers the main microcontroller, which runs FreeRTOS and owns real-time control and safety, plus the smaller peripheral chips it drives, which run bare-metal C.

### Safety

Safety is enforced from the bottom up, and the backend and network are never part of the safety path.

- The controller sends the main microcontroller a periodic heartbeat. If heartbeats stop, the microcontroller brings the motors to a stop.
- Each peripheral chip applies the same rule to commands from the main microcontroller.
- A physical e-stop cuts motor power through a relay, independent of all software.

## Repo layout

Turborepo monorepo. Only `frontend/` is live today, and it is the only pnpm workspace package. The other folders will build with their own toolchains.

| Folder | Status | Notes |
| :--- | :--- | :--- |
| `frontend/` | Live | Vite + React 19 + R3F SPA |
| `backend/` | Placeholder | Kotlin telemetry service (monolith) |
| `controller/` | Placeholder | Linux + ROS 2 onboard computer |
| `firmware/` | Placeholder | FreeRTOS C++ main MCU, bare-metal C peripheral chips |
| `shared/` | Placeholder | Cross-language protocol and message definitions |

## Local development

Requires Node 20.11.1 and pnpm 9.15.9.

```powershell
pnpm install
pnpm dev      # frontend at http://localhost:5173/
pnpm build    # production build
pnpm lint     # eslint across workspace
```

## CI / deploy

GitHub Actions runs lint + build on every PR and push to `main`. Pushes to `main` auto-deploy the frontend to GitHub Pages.

See `.github/workflows/ci.yml`.

## Stack

| Layer | Tool |
| :--- | :--- |
| Monorepo | Turborepo + pnpm workspaces |
| Bundler | Vite 6 |
| Frontend | React 19 + TypeScript 5.8 |
| Styling | Tailwind CSS 4 |
| Routing | TanStack Router (file-based) |
| 3D | three + @react-three/fiber + drei |
