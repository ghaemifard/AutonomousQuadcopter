# Autonomous Person-Following Quadcopter

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![MAVSDK](https://img.shields.io/badge/MAVSDK-PX4-blue)](https://mavsdk.mavlink.io/)
[![YOLOv4](https://img.shields.io/badge/YOLOv4-Darknet-orange)](https://github.com/AlexeyAB/darknet)

An experimental autonomous quadcopter platform that combines **computer vision**, **MAVLink-based flight control**, and **real-time video streaming** to detect and follow a person.

> **Project Status:** Experimental / Research

## Overview

This project aims to build an **autonomous quadcopter** capable of **detecting and following a person** with minimal human intervention.

The system runs on a **NVIDIA Jetson Nano** connected to a **Pixhawk Cube** flight controller. It combines:
- Real-time **YOLOv4-tiny** object detection (CUDA accelerated)
- PID-based visual tracking
- MAVSDK / DroneKit for flight control (manual + offboard modes)
- Live video streaming via Flask

---

## 🎯 Project Goal

Build a fully autonomous person-following drone that can:
- Detect a person using computer vision
- Automatically adjust yaw/pitch to track and follow the target
- Support manual override via laptop
- Stream live video to a browser

---

## Hardware Requirements

- **Jetson Nano** (or compatible Jetson device)
- **Pixhawk Cube** (or any PX4/ArduPilot compatible flight controller)
- USB connection between Jetson and Pixhawk (`/dev/ttyACM0`)
- CSI Camera (Raspberry Pi / IMX219 or similar)
- Strong **WiFi dongle** on Jetson Nano
- RC Transmitter (for emergency manual control)
- Power bank for Jetson nano / LiPo battery setup

**Recommended Connectivity**:  
Connect your laptop and Jetson Nano via **smartphone hotspot** for stable communication.

---

## Features

- **Person Detection**: YOLOv4-tiny with CUDA support
- **Autonomous Tracking**: PID controller for yaw (and optional pitch)
- **Manual Control**: Keyboard commands or socket-based remote control
- **Flight Modes**: Stabilize, Land, Hold, RTL, Offboard, etc.
- **Live Video Streaming**: Accessible at `http://<JETSON_IP>:8008`
- **Calibration Support**: Gyro, level, pressure
- **Safety**: Arm/Disarm, Kill, timeouts

---

## Important Notes

- **When using laptop control**, the physical RC transmitter **stops working** (RC overrides are active).
- **Always calibrate gyro and level** before arming the drone.
- Python loops are slow on Jetson Nano → **Train a custom YOLO model with ≤5 classes** for better performance.
- It is **highly recommended** to train your own YOLO model on your specific environment and target.

---

## Supported Commands (via Keyboard / Socket)

| Command          | Action                              |
|------------------|-------------------------------------|
| `Space`          | Arm                                 |
| `Esc`            | Disarm + Kill                       |
| Arrow Keys       | Throttle / Yaw                      |
| `W` / `S`        | Pitch Up / Down                     |
| `A` / `D`        | Roll Left / Right                   |
| `1-8`            | Change throttle levels / modes      |
| `m`              | Toggle distance sensor + height hold|
| `g` / `h`        | Start / Stop manual computer control|
| `l` / `k`        | Start / Stop camera detection       |
| Calibration keys | Gyro, Level, etc.                   |

---

 

## Software Stack

- Python
- OpenCV
- YOLOv4-tiny
- MAVSDK
- DroneKit
- PyMAVLink
- Flask
- SimplePID

---

## Repository Structure

```
.
├── MyVehicle.py          # DroneKit implementation
├── MavVehicle.py         # MAVSDK implementation
├── YoloDetection.py      # YOLOv4 detector
├── videoSharing.py       # Video streaming
├── newm/                 # New modular implementation
├── nutty/                # Experimental version
└── off/                  # Legacy implementation
```
The repository contains multiple experimental implementations. The `newm` directory represents the newer and more modular architecture.

---

## Installation

Install the required Python packages:

```bash
pip install \
    mavsdk \
    dronekit \
    flask \
    opencv-python \
    simple-pid \
    readchar
```

Connect the Pixhawk via USB (typically `/dev/ttyACM0`) and update the connection string or model paths in the source code.

To start video streaming:

```bash
python videoSharing.py
```


or use the corresponding implementation inside `newm/` if applicable.


---

## Video Streaming

The onboard camera stream can be viewed from any browser on the same network.

```
http://<JETSON_IP>:8008
```

Replace `<JETSON_IP>` with the IP address of the Jetson Nano.

---

## Object Detection

Object detection is performed using **YOLOv4-tiny**.

Although pretrained models can be used, training a custom model for your specific environment is strongly recommended.

Since the Jetson Nano has limited computational resources, keeping the number of object classes below **five** significantly improves inference speed.

---

## Notes

When computer control is active, RC override commands are continuously sent to the flight controller. During this time, the physical RC transmitter may not have control authority until software control is disabled.

Always verify flight behavior in a safe environment before enabling autonomous features.

---

## Disclaimer

This project is intended for research and educational purposes.

Flight testing autonomous drones involves significant risks. Always test in a safe open area, keep a pilot ready to take over, and comply with local UAV regulations.
