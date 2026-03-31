# Bin Picking Robot

Vision-guided Cartesian gantry robot for automated pick-and-place of poker chips using an overhead camera and vertical suction end effector.

## Why this project
This project is designed to mimic real industrial pick-and-place automation systems rather than a generic hobby robot arm. A Cartesian gantry was chosen because it is mechanically simple, precise, scalable, and common in manufacturing automation.

## System Overview
- Overhead camera detects poker chip positions
- Vision system outputs image coordinates
- Calibration converts image coordinates to workspace coordinates
- Gantry moves in X/Y/Z to target
- Suction end effector picks and places chip into drop zone

## Mechanical Architecture
- Cartesian gantry
- Belt-driven X/Y axes
- Lead-screw-driven Z axis
- Fixed overhead camera
- Vertical suction pickup

## Software Architecture
- `vision/` for perception
- `control/` for planning and motion logic
- `hardware/` for actuator interfaces

## Current Status
- Initial gantry CAD concept completed
- Project folder structure created
- Starter software architecture created

## Next Steps
1. Get camera feed running
2. Detect poker chips with OpenCV
3. Visualize detections
4. Implement basic pixel-to-world calibration
5. Simulate pick-and-place flow
6. Integrate hardware later

## Future Upgrades
- ROS2 node architecture
- Multi-object sorting
- Conveyor-based picking
- Failed-pick handling
- More advanced calibration
