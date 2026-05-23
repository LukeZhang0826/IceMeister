# controller

Runtime orchestration layer sitting between `firmware` and `backend`.
Likely responsibilities:

- Real-time control loop
- Sensor fusion (IMU, encoders, lidar/depth if added)
- Path planning and rink-edge tracking
- Bridge between firmware (serial / CAN / UART) and backend (network)

**Status:** placeholder. Hardware target and language not yet chosen.

**Likely candidates:**
- Raspberry Pi 4/5 or Jetson Nano running:
  - Python + ROS 2
  - Rust (for tighter latency / no GIL)

Not part of the pnpm workspace.
