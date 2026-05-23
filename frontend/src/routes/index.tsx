import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/')({
  component: HomePage,
})

function HomePage() {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <p className="text-ink-muted text-sm tracking-widest uppercase">
        IceMeister — landing page placeholder
      </p>
    </main>
  )
}
