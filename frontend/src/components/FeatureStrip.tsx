const features = [
  {
    label: '01',
    title: 'Autonomous',
    body: 'On-board pathing tracks rink geometry without a driver. Designed for repeatable, edge-aware coverage.',
  },
  {
    label: '02',
    title: 'Compact',
    body: 'Footprint sized for community rinks, training pads, and tight indoor surfaces where full-scale machines do not fit.',
  },
  {
    label: '03',
    title: 'Electric',
    body: 'Quiet, emission-free drivetrain. Built for residential and indoor operation without exhaust handling.',
  },
]

export function FeatureStrip() {
  return (
    <section
      id="features"
      className="px-8 py-28 border-t border-border"
    >
      <div className="max-w-6xl mx-auto">
        <p className="text-xs tracking-[0.3em] uppercase text-ink-muted mb-12">
          Specifications
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-x-12 gap-y-16">
          {features.map((f) => (
            <div key={f.title}>
              <p className="font-mono text-xs text-accent mb-4">{f.label}</p>
              <h3 className="text-2xl font-medium mb-3">{f.title}</h3>
              <p className="text-ink-muted leading-relaxed">{f.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
