# shared

Code shared across multiple workspaces — typically types, schemas,
protocol definitions, and constants.

**Status:** placeholder. Language not yet chosen.

**Likely shape depending on stack choice:**
- TypeScript package (added to `pnpm-workspace.yaml`, consumed by
  `frontend` and a TS `backend`)
- Protobuf or JSON Schema definitions with codegen scripts invoked
  from each language's build pipeline (cross-language)

Pick one once `backend` and `controller` languages are committed.
