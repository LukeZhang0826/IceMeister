# frontend

IceMeister's single-page app. Today it is the landing page. It will also become the interface for vehicle telemetry and status.

**Status:** live at https://icemeister.ca/

**Stack:** Vite, React 19, TypeScript, Tailwind CSS 4, TanStack Router and Query, three + @react-three/fiber + drei.

The frontend only talks to `backend`. It never connects to the vehicle directly.

## Development

Run from the repo root:

```powershell
pnpm install
pnpm dev      # http://localhost:5173/
pnpm build
pnpm lint
```

Pushes to `main` auto-deploy to GitHub Pages. See `.github/workflows/ci.yml`.
