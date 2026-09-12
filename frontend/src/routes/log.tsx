import { createFileRoute, Link } from '@tanstack/react-router'
import {
  entries,
  isMemberId,
  members,
  type LogEntry,
  type MemberId,
} from '../data/designLog'

type LogSearch = {
  member?: MemberId
}

export const Route = createFileRoute('/log')({
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

  const visible = entries
    .filter((e) => !selected || e.member === selected)
    .sort((a, b) => b.date.localeCompare(a.date))

  return (
    <main className="min-h-full px-8 py-24">
      <div className="max-w-5xl mx-auto">
        <p className="text-xs tracking-[0.3em] uppercase text-ink-muted mt-16 mb-6">
          Design Log
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
              count={entries.filter((e) => e.member === m.id).length}
              active={selected === m.id}
              search={{ member: m.id }}
            />
          ))}
        </nav>

        <ol className="mt-16 border-t border-border">
          {visible.map((entry) => (
            <Entry
              key={`${entry.date}-${entry.member}-${entry.title}`}
              entry={entry}
            />
          ))}
        </ol>

        {visible.length === 0 && (
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

function Entry({ entry }: { entry: LogEntry }) {
  const member = members.find((m) => m.id === entry.member)

  return (
    <li className="grid md:grid-cols-[10rem_1fr] gap-x-8 gap-y-2 py-10 border-b border-border">
      <div>
        <time dateTime={entry.date} className="font-mono text-sm text-ink-muted">
          {formatDate(entry.date)}
        </time>
      </div>
      <div>
        <p className="text-sm">
          <span className="text-accent">{member?.name}</span>
          <span className="text-ink-muted"> · {member?.role}</span>
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
