export const members = [
  { id: 'tommy', name: 'Tommy F.', role: 'Embedded Electrical' },
  { id: 'nikolai', name: 'Nikolai J.', role: 'Mechanical' },
  { id: 'dheiksha', name: 'Dheiksha J.', role: 'Mechanical' },
  { id: 'josh', name: 'Josh L.', role: 'Embedded Electrical' },
  { id: 'luke', name: 'Luke Z.', role: 'Embedded Software' },
] as const

export type Member = (typeof members)[number]
export type MemberId = Member['id']

export type LogEntry = {
  // YYYY-MM-DD
  date: string
  member: MemberId
  title: string
  // Blank lines separate paragraphs.
  body: string
}

// Add new entries anywhere in this list. The log page sorts them by date.
export const entries: LogEntry[] = [
  {
    date: '2026-09-12',
    member: 'luke',
    title: 'Narrowed down the system architecture',
    body: `Split the system into layers that each run on their own hardware. The main microcontroller runs FreeRTOS in C++ and drives a set of smaller peripheral chips running bare-metal C. An onboard Linux computer running ROS 2 handles autonomy and connects to a Kotlin telemetry backend, which starts as a monolith. The frontend stays a single-page app that only talks to the backend.

Safety is enforced from the bottom up. The main microcontroller stops the motors if heartbeats from the Linux computer stop, each peripheral chip does the same for the microcontroller, and a physical e-stop cuts motor power independent of all software.`,
  },
]

export function isMemberId(value: unknown): value is MemberId {
  return members.some((m) => m.id === value)
}
