import { createRootRoute, HeadContent, Outlet } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { NavBar } from '../components/NavBar'

export const Route = createRootRoute({
  // Default document title. Child routes override it by returning their own.
  head: () => ({ meta: [{ title: 'Ice Meister' }] }),
  component: RootLayout,
})

function RootLayout() {
  return (
    <>
      <HeadContent />
      <NavBar />
      <Outlet />
      {import.meta.env.DEV && (
        <>
          <TanStackRouterDevtools position="bottom-right" />
          <ReactQueryDevtools initialIsOpen={false} buttonPosition="bottom-left" />
        </>
      )}
    </>
  )
}
