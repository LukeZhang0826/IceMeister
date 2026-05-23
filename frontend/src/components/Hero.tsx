import { ZambonScene } from './ZambonScene'

export function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col">
      <div className="px-8 pt-24 pb-6 max-w-6xl mx-auto w-full">
        <p className="text-xs tracking-[0.3em] uppercase text-ink-muted mb-6">
          Autonomous Ice Resurfacing
        </p>
        <h1 className="text-6xl md:text-8xl font-semibold tracking-tight leading-none">
          Ice<span className="text-accent">Meister</span>
        </h1>
        <p className="mt-6 text-lg text-ink-muted max-w-xl leading-relaxed">
          A compact, autonomous zamboni built for small rinks where full-scale
          machines do not fit.
        </p>
      </div>

      <div className="flex-1 min-h-[420px]">
        <ZambonScene />
      </div>

      <div className="px-8 pb-16 max-w-6xl mx-auto w-full flex items-center gap-4">
        <a
          href="#features"
          className="inline-flex items-center gap-2 px-6 py-3 bg-accent text-bg font-medium rounded-sm hover:opacity-90 transition"
        >
          Learn more
        </a>
        <span className="text-xs font-mono uppercase tracking-widest text-ink-muted">
          v0.0.0 · prototype
        </span>
      </div>
    </section>
  )
}
