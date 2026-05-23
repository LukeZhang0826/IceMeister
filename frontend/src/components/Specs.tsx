type SpecGroup = {
  group: string
  rows: Array<[string, string]>
}

const specs: SpecGroup[] = [
  {
    group: 'Dimensions',
    rows: [
      ['Length', '1.4 m'],
      ['Width', '0.9 m'],
      ['Height', '1.1 m'],
      ['Operating weight', '127 kg'],
      ['Cutting width', '850 mm'],
    ],
  },
  {
    group: 'Power',
    rows: [
      ['Battery', 'LiFePO₄, 36 V · 50 Ah'],
      ['Runtime', '90 min'],
      ['Charge time', '45 min · L1 110 V'],
      ['Drivetrain', 'Dual brushless hub motors'],
      ['Top speed', '8 km/h'],
    ],
  },
  {
    group: 'Perception & Compute',
    rows: [
      ['Lidar', '360° solid-state, 25 m range'],
      ['Cameras', 'Stereo RGB, front-facing'],
      ['Compute', 'ARM Cortex-A78 + 6 TOPS NPU'],
      ['Connectivity', 'Wi-Fi 6, Bluetooth 5.3, LTE backup'],
      ['Operating temperature', '−20 °C to +5 °C ambient'],
    ],
  },
  {
    group: 'Resurfacing',
    rows: [
      ['Blade depth', '0.5 – 3.0 mm, programmable'],
      ['Water tank', '18 L'],
      ['Edge tolerance', '± 5 mm'],
      ['Coverage', '75 sq ft / min'],
      ['Pass overlap', '50 mm default, adjustable'],
    ],
  },
]

export function Specs() {
  return (
    <section className="border-t border-border bg-surface px-8 py-32">
      <div className="max-w-7xl mx-auto">
        <p className="text-xs tracking-[0.3em] uppercase text-ink-muted mb-16">
          Specifications
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-16 gap-y-20">
          {specs.map((g) => (
            <div key={g.group}>
              <h3 className="text-xl font-medium mb-6">{g.group}</h3>
              <dl className="divide-y divide-border">
                {g.rows.map(([k, v]) => (
                  <div
                    key={k}
                    className="flex items-center justify-between py-3 gap-4"
                  >
                    <dt className="text-sm text-ink-muted">{k}</dt>
                    <dd className="font-mono text-sm text-right">{v}</dd>
                  </div>
                ))}
              </dl>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
