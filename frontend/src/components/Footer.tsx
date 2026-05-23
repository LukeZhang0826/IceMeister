const cols = [
  {
    heading: 'Product',
    items: ['Overview', 'Specifications', 'Process', 'Roadmap'],
  },
  {
    heading: 'Company',
    items: ['About', 'Team', 'Careers', 'Press'],
  },
  {
    heading: 'Contact',
    items: ['Sales', 'Support', 'Partnerships', 'Media'],
  },
]

export function Footer() {
  return (
    <footer className="border-t border-border px-8 py-20">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-x-8 gap-y-12 mb-16">
          <div>
            <p className="text-lg font-semibold">
              Ice<span className="text-accent">Meister</span>
            </p>
            <p className="text-sm text-ink-muted mt-3 max-w-xs leading-relaxed">
              Autonomous ice resurfacing, built for the rinks the big machines
              forgot.
            </p>
          </div>
          {cols.map((col) => (
            <div key={col.heading}>
              <h4 className="text-xs tracking-widest uppercase text-ink-muted mb-4">
                {col.heading}
              </h4>
              <ul className="space-y-2">
                {col.items.map((item) => (
                  <li key={item}>
                    <a
                      href="#"
                      className="text-sm hover:text-accent transition"
                    >
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="flex items-center justify-between text-xs text-ink-muted border-t border-border pt-8">
          <span>© {new Date().getFullYear()} IceMeister</span>
          <span className="font-mono uppercase tracking-widest">
            Prototype · v0.0.0
          </span>
        </div>
      </div>
    </footer>
  )
}
