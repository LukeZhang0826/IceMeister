const stats = [
  { value: '127', unit: 'kg', label: 'Operating weight' },
  { value: '90', unit: 'min', label: 'Runtime per charge' },
  { value: '75', unit: 'ft²/min', label: 'Resurface coverage' },
  { value: '0.9', unit: 'm', label: 'Turning radius' },
]

export function Stats() {
  return (
    <section className="border-t border-border px-8 py-24">
      <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-x-8 gap-y-12">
        {stats.map((s) => (
          <div key={s.label}>
            <div className="flex items-baseline gap-2">
              <span className="text-5xl md:text-6xl font-semibold tracking-tight tabular-nums">
                {s.value}
              </span>
              <span className="font-mono text-sm text-ink-muted">{s.unit}</span>
            </div>
            <p className="mt-3 text-xs tracking-widest uppercase text-ink-muted">
              {s.label}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}
