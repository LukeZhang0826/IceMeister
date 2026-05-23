const capabilities = [
  {
    label: '01',
    title: 'Perception',
    body: 'A 360° solid-state lidar continuously maps the rink boundary and detects skaters, equipment, and rink debris. Onboard inference runs at 30 Hz on a low-power compute module — no cloud dependency, no network latency, no privacy trade-off.',
  },
  {
    label: '02',
    title: 'Drivetrain',
    body: 'Two independently-driven brushless hub motors deliver differential steering and a true zero-radius turn. Regenerative braking returns energy to the pack on every deceleration, extending runtime by an estimated 14% on the same charge.',
  },
  {
    label: '03',
    title: 'Resurfacing',
    body: 'A precision-controlled blade carriage shaves the ice to programmable depth between 0.5 and 3.0 mm, while heated water laid behind it freezes into a fresh top layer. Edge tracking holds the blade within ±5 mm of the perimeter on irregular rinks.',
  },
]

export function Capabilities() {
  return (
    <section
      id="capabilities"
      className="border-t border-border px-8 py-32"
    >
      <div className="max-w-7xl mx-auto">
        <p className="text-xs tracking-[0.3em] uppercase text-ink-muted mb-16">
          Capabilities
        </p>
        <div className="grid grid-cols-1 gap-24">
          {capabilities.map((c) => (
            <div
              key={c.title}
              className="grid grid-cols-1 md:grid-cols-12 gap-8"
            >
              <div className="md:col-span-3">
                <p className="font-mono text-accent text-sm">{c.label}</p>
                <h3 className="text-3xl font-medium mt-2">{c.title}</h3>
              </div>
              <p className="md:col-span-8 md:col-start-5 text-ink-muted text-lg leading-relaxed">
                {c.body}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
