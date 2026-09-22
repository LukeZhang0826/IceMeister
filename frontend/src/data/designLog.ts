import Papa from 'papaparse'

export const members = [
  { id: 'tommy', name: 'Tommy F.', role: 'Embedded Electrical' },
  { id: 'nikolai', name: 'Nikolai J.', role: 'Mechanical' },
  { id: 'dheiksha', name: 'Dheiksha J.', role: 'Mechanical' },
  { id: 'josh', name: 'Josh L.', role: 'Embedded Electrical' },
  { id: 'luke', name: 'Luke Z.', role: 'Embedded Software' },
] as const

export type Member = (typeof members)[number]
export type MemberId = Member['id']

export type LogEntry = {
  // YYYY-MM-DD
  date: string
  // Everyone who took part: one id for solo work, several for a group session.
  members: MemberId[]
  title: string
  // Blank lines separate paragraphs.
  body: string
}

// A row the sheet gave us that we could not turn into a LogEntry. Surfaced on
// the page so whoever typed it can see the mistake without reading a console.
export type SkippedRow = {
  // 1-based, counting the header as row 1, so it matches the Sheets gutter.
  row: number
  reason: string
}

export type DesignLog = {
  entries: LogEntry[]
  skipped: SkippedRow[]
}

export function isMemberId(value: unknown): value is MemberId {
  return members.some((m) => m.id === value)
}

export function memberName(id: MemberId) {
  return members.find((m) => m.id === id)!.name
}

const DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/
const MEMBER_IDS = members.map((m) => m.id).join(', ')

type RowResult =
  | { ok: true; entry: LogEntry }
  | { ok: false; reason: string }

// Every cell arrives as a string, so nothing is trusted until it is checked here.
function toEntry(row: Record<string, string | undefined>): RowResult {
  const date = (row.date ?? '').trim()
  const title = (row.title ?? '').trim()
  // Sheets returns CRLF inside multi-line cells; the paragraph split wants LF.
  const body = (row.body ?? '').replace(/\r\n/g, '\n').trim()

  if (!DATE_PATTERN.test(date) || Number.isNaN(Date.parse(date))) {
    return { ok: false, reason: `date must be YYYY-MM-DD, got "${date}"` }
  }

  const raw = (row.members ?? '')
    .split(',')
    .map((id) => id.trim().toLowerCase())
    .filter(Boolean)

  if (raw.length === 0) {
    return { ok: false, reason: `members is empty, expected one or more of ${MEMBER_IDS}` }
  }

  const unknown = raw.filter((id) => !isMemberId(id))
  if (unknown.length > 0) {
    return { ok: false, reason: `unknown member ${unknown.join(', ')}, expected ${MEMBER_IDS}` }
  }

  // Keep the order the members list declares so attendee lists read consistently.
  const present = members.map((m) => m.id).filter((id) => raw.includes(id))

  if (!title) {
    return { ok: false, reason: 'title is empty' }
  }
  if (!body) {
    return { ok: false, reason: 'body is empty' }
  }

  return { ok: true, entry: { date, members: present, title, body } }
}

export async function fetchDesignLog(): Promise<DesignLog> {
  const url = import.meta.env.VITE_DESIGN_LOG_CSV_URL
  if (!url) {
    throw new Error(
      'VITE_DESIGN_LOG_CSV_URL is not set. Add the published sheet CSV URL to frontend/.env.',
    )
  }

  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(`Sheet request failed with ${response.status} ${response.statusText}`)
  }

  // Google prefixes the export with a byte order mark that would otherwise end
  // up glued to the first header name.
  const csv = (await response.text()).replace(/^\uFEFF/, '')
  const parsed = Papa.parse<Record<string, string | undefined>>(csv, {
    header: true,
    skipEmptyLines: true,
    transformHeader: (header) => header.trim().toLowerCase(),
  })

  const entries: LogEntry[] = []
  const skipped: SkippedRow[] = []

  parsed.data.forEach((row, i) => {
    const result = toEntry(row)
    if (result.ok) {
      entries.push(result.entry)
    } else {
      skipped.push({ row: i + 2, reason: result.reason })
    }
  })

  for (const error of parsed.errors) {
    skipped.push({
      row: typeof error.row === 'number' ? error.row + 2 : 0,
      reason: error.message,
    })
  }

  entries.sort((a, b) => b.date.localeCompare(a.date))
  skipped.sort((a, b) => a.row - b.row)

  return { entries, skipped }
}
