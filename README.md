# IceMeister

Autonomous small zamboni. Built for community rinks, training facilities, and backyard installations the big machines can't reach.

> Product name tentative. Specs, copy, and the 3D model on the landing page are placeholder while the hardware is in design.

**Live site:** https://lukezhang0826.github.io/IceMeister/

---

## Repo layout

Turborepo monorepo. Only `frontend/` is live today.

| Folder | Status | Notes |
| :--- | :--- | :--- |
| `frontend/` | Live | Vite + React 19 + R3F landing page |
| `backend/` | Placeholder | Language TBD |
| `controller/` | Placeholder | Language TBD |
| `firmware/` | Placeholder | Language TBD |
| `shared/` | Placeholder | Language TBD |

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
