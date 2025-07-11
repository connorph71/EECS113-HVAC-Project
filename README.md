# 🌡️ **EECS113-HVAC-Project**

A real-time embedded HVAC system developed on Raspberry Pi using C and Python. Designed to monitor and control temperature and motion using peripheral sensors. This project was built as a final solo project for EECS 113: Processor Hardware/Software Interaction at the University of California, Irvine.

---
## 🔌 **Technologies Used**

- Languages: Python
- Platform: Raspberry Pi (Raspbian OS)
- Concepts: RTOS-inspired task scheduling, multithreading, GPIO control
- Sensors: DHT11 (temperature/humidity), PIR motion sensor
- Display: LCD module, LEDs
- Tools: GPIO libraries, basic oscilloscope for signal testing
---
## 📋 **Project Features:**
- Manual data input via buttons
- Motion detection using PIR sensor
- Periodic temperature and humidity monitoring
- Automatic state transitions for Heater/AC modes based on sensor data
- Real-time data display via LCD showing:
  - Time
  - Current & Desired Temperatures
  - HVAC Status
  - Door/Window Status
  - Security/Fire Alarm Status
  - Light Status
- Multithreaded architecture simulating RTOS behavior
- Log file creation

---
## 💻 **Architecture**

          ┌────────────────────────────┐
          │        Main Thread         │
          │  - Initializes all threads │
          │  - Monitors system state   │
          └────────────┬───────────────┘
                       │
           ┌───────────┴──────────────────┐
           ▼                              ▼
      LCD Display Thread             Daemon Threads
      (Primary update loop)        ┌────────────────┐
                                   │ - PIR Sensor   │
                                   │ - DHT11 Sensor │
                                   │ - Button Input │
                                   └────────────────┘
