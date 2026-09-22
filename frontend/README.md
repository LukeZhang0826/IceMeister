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

## Design log

`/log` reads its entries at runtime from a Google Sheet that the whole team can
edit, so nobody needs git to add one. The sheet is published to the web as CSV
and its URL lives in `.env` as `VITE_DESIGN_LOG_CSV_URL`.

Columns, exactly these four headers in row 1:

| column | value |
| --- | --- |
| `date` | `YYYY-MM-DD`, with the column formatted as plain text so Sheets does not rewrite it |
| `members` | one or more ids from `src/data/designLog.ts`, comma separated; several ids means a group session |
| `title` | one line |
| `body` | free text, blank lines separate paragraphs |

Rows that do not match are dropped and listed on the page with the reason and
the sheet row number. Adding a teammate means adding them to `members` in
`src/data/designLog.ts`, which is the only part still hardcoded.
