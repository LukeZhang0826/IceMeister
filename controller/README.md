# controller

IceMeister's onboard computer. Sits between `firmware` and `backend`.

**Status:** placeholder. Exact board not yet chosen.

**Stack:** Linux running ROS 2.

Responsibilities:

- Autonomy: sensor fusion, localization, path planning, and rink-edge tracking
- Send motion commands to the main microcontroller in `firmware` over serial or CAN
- Send a periodic heartbeat to the main microcontroller so it can stop the vehicle if the controller hangs
- Relay telemetry to `backend` over the network, buffering it when the connection drops

Real-time motor control and safety interlocks live in `firmware`, not here.

Not part of the pnpm workspace.
