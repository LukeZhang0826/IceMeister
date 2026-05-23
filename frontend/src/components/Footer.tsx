export function Footer() {
  return (
    <footer className="px-8 py-10 border-t border-border">
      <div className="max-w-6xl mx-auto flex items-center justify-between text-sm text-ink-muted">
        <span>© {new Date().getFullYear()} IceMeister</span>
        <span className="font-mono uppercase tracking-widest text-xs">
          Prototype · v0.0.0
        </span>
      </div>
    </footer>
  )
}
