export function Hero() {
  return (
    <section className="relative h-screen overflow-hidden bg-bg">
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{ backgroundImage: "url('/images/Surfaceuse.jpg')" }}
        aria-hidden
      />
      <div
        className="absolute inset-0"
        style={{
          background:
            'linear-gradient(to bottom, rgba(10,10,11,0.35) 0%, rgba(10,10,11,0.45) 30%, rgba(10,10,11,0.85) 65%, #0a0a0b 95%)',
        }}
        aria-hidden
      />

      <div className="relative h-full max-w-7xl mx-auto px-8 flex flex-col">
        <div className="pt-24">
          <p className="text-xs tracking-[0.3em] uppercase text-ink-muted mb-6">
            Autonomous Ice Resurfacing
          </p>
          <h1 className="text-7xl md:text-9xl font-semibold tracking-tight leading-none">
            Ice<span className="text-accent">Meister</span>
          </h1>
          <p className="mt-6 text-lg text-ink-muted max-w-xl leading-relaxed">
            A compact, autonomous resurfacer designed for community rinks,
            training facilities, and backyard installations the big machines
            cannot reach.
          </p>
        </div>

        <div className="mt-auto pb-12 flex items-end justify-between">
          <a
            href="#machine"
            className="inline-flex items-center gap-2 px-6 py-3 bg-accent text-bg font-medium rounded-sm hover:opacity-90 transition"
          >
            See the machine
          </a>
          <span className="font-mono uppercase tracking-widest text-xs text-ink-muted">
            scroll ↓
          </span>
        </div>
      </div>
    </section>
  )
}
