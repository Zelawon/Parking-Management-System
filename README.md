# Parking Management System (Simulation)

## Overview

The **Parking Management System** is a simulation-based project that automates and optimizes parking lot operations using MQTT, Node-RED, and Python. 
It visualizes parking slot availability in real time and categorizes occupancy by floors and vehicle types.

---

## Features

- **Vehicle Selection:** Users can choose vehicle types (motorcycle, car, electric) via `parking_manager.py`.
- **Real-time Display:** Updates on slot availability are managed by `parking_status_display.py`.
- **Node-RED Dashboard:** Displays parking slot availability per floor and vehicle type, including gauges for category-specific occupancy percentages.
- **Simulated Environment:** No physical sensors; all data is simulated using Python scripts and MQTT.

---

## Files

1. **`flows.json`**  
   - Node-RED flow configuration to display parking slot availability and occupancy percentages on a dashboard.

2. **`parking_manager.py`**  
   - Simulates user input for vehicle type and sends MQTT messages to update parking slot status.

3. **`parking_status_display.py`**  
   - Displays all available parking spots by subscribing to MQTT topics and outputting slot status in real-time.

---

## Installation

### Clone the repository

```bash
   git clone https://github.com/Zelawon/Parking-Management-System.git
   cd smart-parking-management-system
```
### Install dependencies

**Update Your System**
```bash
sudo apt update && sudo apt upgrade -y
```

**Mosquitto MQTT Broker**
```bash
sudo apt update && sudo apt install mosquitto
```

**Node-RED**
```bash
npm install -g node-red
cd ~/.node-red
npm install node-red-contrib-aedes node-red-dashboard node-red-contrib-web-worldmap
```

**Install Python3**
```bash
sudo apt install -y python3 python3-pip
```

**Install paho-mqtt**
```bash
pip3 install paho-mqtt
```

### Verify the installation

```bash
mosquitto -v
node-red --version
python3 --version
python3 -m pip show paho-mqtt
```

## Usage

**Start the MQTT Broker**
```bash
mosquitto
```

**Run Python Scripts**
```bash
python3 python/parking_manager.py
python3 python/parking_status_display.py
```

**SLaunch Node-RED Dashboard**
```bash
node-red
```
- Access the Node-RED at http://localhost:1880/.
- Access the dashboard at http://localhost:1880/ui.

## License
This project is licensed under the GPL-3.0 License. See the `LICENSE` file for details.
