/// <reference types="vite/client" />

interface ImportMetaEnv {
  // Published-to-web CSV export of the group design log sheet.
  readonly VITE_DESIGN_LOG_CSV_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
