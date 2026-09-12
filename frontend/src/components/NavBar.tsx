import { Link } from '@tanstack/react-router'

const linkClass = 'text-sm transition'
const activeProps = { className: 'text-ink' }
const inactiveProps = { className: 'text-ink-muted hover:text-ink' }

export function NavBar() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-border bg-bg/70 backdrop-blur">
      <nav className="max-w-7xl mx-auto px-8 h-16 flex items-center justify-between">
        <Link to="/" className="text-lg font-semibold">
          Ice<span className="text-accent">Meister</span>
        </Link>
        <div className="flex items-center gap-8">
          <Link
            to="/"
            className={linkClass}
            activeOptions={{ exact: true }}
            activeProps={activeProps}
            inactiveProps={inactiveProps}
          >
            Home
          </Link>
          <Link
            to="/log"
            className={linkClass}
            activeOptions={{ includeSearch: false }}
            activeProps={activeProps}
            inactiveProps={inactiveProps}
          >
            Design Log
          </Link>
        </div>
      </nav>
    </header>
  )
}
