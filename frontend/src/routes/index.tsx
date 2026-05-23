import { createFileRoute } from '@tanstack/react-router'
import { Hero } from '../components/Hero'
import { FeatureStrip } from '../components/FeatureStrip'
import { Footer } from '../components/Footer'

export const Route = createFileRoute('/')({
  component: HomePage,
})

function HomePage() {
  return (
    <>
      <Hero />
      <FeatureStrip />
      <Footer />
    </>
  )
}
