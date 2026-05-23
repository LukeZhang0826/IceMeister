import { createFileRoute } from '@tanstack/react-router'
import { Hero } from '../components/Hero'
import { Machine } from '../components/Machine'
import { Stats } from '../components/Stats'
import { Capabilities } from '../components/Capabilities'
import { Specs } from '../components/Specs'
import { Process } from '../components/Process'
import { Footer } from '../components/Footer'

export const Route = createFileRoute('/')({
  component: HomePage,
})

function HomePage() {
  return (
    <>
      <Hero />
      <Machine />
      <Stats />
      <Capabilities />
      <Specs />
      <Process />
      <Footer />
    </>
  )
}
