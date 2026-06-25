# R2Beer2 — Drink-Serving Robot

A mobile robot that autonomously finds people, approaches them, and offers drinks.

## Hardware

| Component | Details |
|---|---|
| Compute | Jetson Orin Nano 8GB |
| Camera | Luxonis OAK-D Pro W (IMX378, 120° DFOV, Myriad X VPU) |
| LiDAR | SICK (761 points, 190° sweep, 0.25°/point) — hardware safety cutoff at 60 cm cuts motor power |
| Motors | Differential drive via USB serial (`/dev/ttyUSB0`, 115200 baud, `r,{left},{right}\n`) |

## Architecture (planned)

```
IDLE → SEARCH → APPROACH → INTERACT → SEARCH / FOLLOW_ME
                                    ↘ LAS_VEGAS
RETURN_DOCK
```

| Mode | Description |
|---|---|
| SEARCH | Slow spin, camera scans for people |
| APPROACH | Steer toward nearest person, stop at ~70 cm |
| INTERACT | MediaPipe gesture recognition (thumbs up = yes, middle finger = no) |
| FOLLOW_ME | Track person at ~100 cm using OAK-D depth |
| LAS_VEGAS | Attract/demo loop with music and movement |
| RETURN_DOCK | Navigate to charging station via ArUco marker |

## Key modules (in development)

```
main.py              — entry point, starts all threads
motor.py             — send_run(left, right) abstraction
lidar.py             — LiDAR reader thread, gap-following steering
camera.py            — DepthAI pipeline, person detection on Myriad X VPU
modes/               — one file per operating mode
voice.py             — offline speech recognition (Vosk)
sounds.py            — audio feedback (pygame)
```

## Legacy code

All original source files are archived in [`v1/`](v1/) — the early webcam + LiDAR experiments that the new architecture is based on.

## Roadmap

See the [GitHub Issues](../../issues) for the full feature backlog across 4 development phases:

- **Phase 1** — Foundation refactor (motor, lidar, camera abstractions)
- **Phase 2** — Core navigation (approach, search, follow-me, area limits)
- **Phase 3** — UI and control (buttons, sounds, LasVegas mode)
- **Phase 4** — Advanced features (docking, voice commands)
