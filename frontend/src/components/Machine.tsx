import { ZambonScene } from './ZambonScene'

export function Machine() {
  return (
    <section id="machine" className="border-t border-border px-8 py-32">
      <div className="max-w-7xl mx-auto">
        <p className="text-xs tracking-[0.3em] uppercase text-ink-muted mb-8">
          The machine
        </p>
        <h2 className="text-4xl md:text-5xl font-medium tracking-tight max-w-2xl mb-16">
          127 kilograms, one purpose.
        </h2>
        <div className="h-[70vh] w-full bg-[#1d1d20] rounded-sm overflow-hidden">
          <ZambonScene />
        </div>
        <p className="mt-6 font-mono text-xs uppercase tracking-widest text-ink-muted">
          Drag to rotate
        </p>
      </div>
    </section>
  )
}
