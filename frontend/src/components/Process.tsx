const steps = [
  {
    label: '01',
    title: 'Scan',
    body: 'Walk the rink once with the setup wand to capture its exact geometry. Stored locally on the unit; no recurring upload required.',
  },
  {
    label: '02',
    title: 'Plan',
    body: 'IceMeister generates a coverage pattern optimized for resurface uniformity and blade wear. Preview and adjust on your phone before the first run.',
  },
  {
    label: '03',
    title: 'Run',
    body: 'Place the unit on the ice, tap start, walk away. Status and live perimeter view sync to the mobile app over local network.',
  },
  {
    label: '04',
    title: 'Report',
    body: 'Each run logs coverage map, ice quality estimate, blade hours, and battery telemetry. Export as PDF or push to your facility log.',
  },
]

export function Process() {
  return (
    <section className="border-t border-border px-8 py-32">
      <div className="max-w-7xl mx-auto">
        <p className="text-xs tracking-[0.3em] uppercase text-ink-muted mb-16">
          How it works
        </p>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
          {steps.map((s) => (
            <div key={s.title}>
              <p className="font-mono text-accent text-sm">{s.label}</p>
              <h3 className="text-2xl font-medium mt-2 mb-4">{s.title}</h3>
              <p className="text-ink-muted leading-relaxed">{s.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
