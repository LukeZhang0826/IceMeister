import { createFileRoute, Link } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import {
  fetchDesignLog,
  isMemberId,
  memberName,
  members,
  type LogEntry,
  type MemberId,
  type SkippedRow,
} from '../data/designLog'

type LogSearch = {
  member?: MemberId
}

export const Route = createFileRoute('/log')({
  head: () => ({ meta: [{ title: 'Design Log' }] }),
  validateSearch: (search: Record<string, unknown>): LogSearch => ({
    member: isMemberId(search.member) ? search.member : undefined,
  }),
  component: LogPage,
})

// Dates are stored as YYYY-MM-DD, which Date parses as UTC midnight.
// Formatting in UTC keeps the displayed day from shifting in local time zones.
function formatDate(date: string) {
  return new Date(date).toLocaleDateString('en-CA', {
    timeZone: 'UTC',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function LogPage() {
  const { member: selected } = Route.useSearch()
  const { data, isPending, isError, error } = useQuery({
    queryKey: ['designLog'],
    queryFn: fetchDesignLog,
    // Poll so an open tab picks up sheet edits without a reload. Google's own
    // cache on the published CSV is the real floor on how fresh this can be.
    staleTime: 10_000,
    refetchInterval: 10_000,
  })

  const entries = data?.entries ?? []
  const visible = entries.filter((e) => !selected || e.members.includes(selected))

  return (
    <main className="min-h-full px-8 py-24">
      <div className="max-w-5xl mx-auto">
        <p className="text-xs tracking-[0.3em] uppercase text-ink-muted mt-16 mb-6">
          Design Log - MTE 481 - Group 31
        </p>
        <h1 className="text-5xl font-semibold tracking-tight">
          Timeline of design work
        </h1>

        <nav className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mt-16">
          <MemberFilter
            label="Everyone"
            sublabel="All work"
            count={entries.length}
            active={!selected}
            search={{}}
          />
          {members.map((m) => (
            <MemberFilter
              key={m.id}
              label={m.name}
              sublabel={m.role}
              count={entries.filter((e) => e.members.includes(m.id)).length}
              active={selected === m.id}
              search={{ member: m.id }}
            />
          ))}
        </nav>

        {data && data.skipped.length > 0 && <SkippedNotice skipped={data.skipped} />}

        <ol className="mt-16 border-t border-border">
          {visible.map((entry) => (
            <Entry
              key={`${entry.date}-${entry.members.join('-')}-${entry.title}`}
              entry={entry}
            />
          ))}
        </ol>

        {isPending && <p className="text-sm text-ink-muted py-12">Loading entries…</p>}

        {isError && (
          <div className="mt-16 rounded-sm border border-border bg-surface px-6 py-5">
            <p className="text-sm">Could not load the design log.</p>
            <p className="font-mono text-xs text-ink-muted mt-2">
              {error instanceof Error ? error.message : String(error)}
            </p>
          </div>
        )}

        {!isPending && !isError && visible.length === 0 && (
          <p className="text-sm text-ink-muted py-12">No entries yet.</p>
        )}
      </div>
    </main>
  )
}

type MemberFilterProps = {
  label: string
  sublabel: string
  count: number
  active: boolean
  search: LogSearch
}

function MemberFilter({ label, sublabel, count, active, search }: MemberFilterProps) {
  return (
    <Link
      to="/log"
      search={search}
      className={`block rounded-sm border px-4 py-3 transition ${
        active
          ? 'border-accent bg-elevated'
          : 'border-border bg-surface hover:border-ink-muted'
      }`}
    >
      <span className="block text-sm font-medium">{label}</span>
      <span className="block text-xs text-ink-muted mt-1">{sublabel}</span>
      <span className="block font-mono text-xs text-ink-muted mt-3">
        {count} {count === 1 ? 'entry' : 'entries'}
      </span>
    </Link>
  )
}

function SkippedNotice({ skipped }: { skipped: SkippedRow[] }) {
  return (
    <div className="mt-8 rounded-sm border border-border bg-surface px-6 py-5">
      <p className="text-sm">
        {skipped.length} {skipped.length === 1 ? 'row' : 'rows'} in the sheet could not be
        read and {skipped.length === 1 ? 'is' : 'are'} not shown below.
      </p>
      <ul className="mt-3 space-y-1 font-mono text-xs text-ink-muted">
        {skipped.map((s) => (
          <li key={`${s.row}-${s.reason}`}>
            {s.row > 0 ? `row ${s.row}: ` : ''}
            {s.reason}
          </li>
        ))}
      </ul>
    </div>
  )
}

function Entry({ entry }: { entry: LogEntry }) {
  const solo = entry.members.length === 1
  const role = solo
    ? members.find((m) => m.id === entry.members[0])?.role
    : `Group session · ${entry.members.length} members`

  return (
    <li className="grid md:grid-cols-[10rem_1fr] gap-x-8 gap-y-2 py-10 border-b border-border">
      <div>
        <time dateTime={entry.date} className="font-mono text-sm text-ink-muted">
          {formatDate(entry.date)}
        </time>
      </div>
      <div>
        <p className="text-sm">
          <span className="text-accent">{entry.members.map(memberName).join(', ')}</span>
          <span className="text-ink-muted"> · {role}</span>
        </p>
        <h2 className="text-2xl font-medium mt-2">{entry.title}</h2>
        <div className="mt-4 space-y-4 text-ink-muted leading-relaxed max-w-3xl">
          {entry.body.split(/\n\s*\n/).map((paragraph, i) => (
            <p key={i}>{paragraph}</p>
          ))}
        </div>
      </div>
    </li>
  )
}
