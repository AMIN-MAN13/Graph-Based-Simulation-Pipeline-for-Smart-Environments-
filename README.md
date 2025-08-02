# 📈 Graph-Based Simulation Pipeline for Smart Environments

This repository contains the full implementation, configurations, and supporting documentation for the Master's thesis:

**📄 Title:** *Transforming Graph Models of Smart Environments for Simulation Purposes*
**🏫 University:** University of Rostock
**👨‍🎓 Author:** Amin Maneshi
**📅 Submission Date:** 26.05.2025
**🔗 Thesis PDF:** [`Masterarbeit_Amin_Maneshi.pdf`](./Masterarbeit_Amin_Maneshi.pdf)

---

## 🔍 Project Overview

This project introduces a **modular and automated simulation pipeline** that transforms **graph-based models** into **fully functional smart environment simulations**. The system is designed to support smart cities, homes, and IoT-based environments using decentralized architectures.

### Key Contributions

* **End-to-end transformation** from abstract graph models to live simulations
* **Schema-driven data generation** and behavior control using JSON Schema
* **VM-based node deployment** via VirtualBox and SSH automation
* **Microservice simulation** using Flask + MariaDB for each node
* **Dynamic inter-node messaging** through REST APIs
* **Support for runtime SQL queries** between nodes

---

## 📂 Repository Contents

```bash
.
├── main.py                       # Main orchestration script
├── Masterarbeit_Amin_Maneshi.pdf  # Final thesis document
├── network_config.json          # Smart environment topology definition
├── config2.json                 # Alternative simulation configuration
├── type1.json / type2.json / type3.json     # Schemas for traffic simulation nodes
├── kitchen_schema.json / livingroom_schema.json
├── kidsroom_schema.json / masterbedroom_schema.json  # Schemas for smart home rooms
├── 12.json / 13.json            # Sample runtime data
```

---

## 🚀 How the System Works

### ✅ Step-by-Step Pipeline

1. **Model the environment** using `network_config.json` and node-specific schemas.
2. **Run `main.py`** to parse configs and construct the simulation graph.
3. **Provision VMs**: Each node is launched as a separate VirtualBox VM.
4. **Deploy Flask services**: Flask APIs run in each VM, serving RESTful endpoints.
5. **Generate and post sensor data** based on the schemas.
6. **Establish inter-node communication** using structured JSON messages.
7. **Issue SQL queries** across the distributed environment for evaluation.

---

## 🌍 Use Cases & Scenarios

### 1. 🏍️ Urban Traffic Management

* Node types: Highway, Crossroad, Train Detector
* Edge logic: Emergency alerts, train signals, CO2 broadcast
* Goal: Simulate traffic behavior with localized and global coordination

### 2. 🏡 Smart Home Automation

* Node types: Kitchen, Living Room, Master Bedroom, Kids Room
* Edge logic: Status updates, safety alerts, motion detection
* Goal: Evaluate room-to-room communication and environmental sensing

---

## ✨ Features

| Feature                        | Description                                                          |
| ------------------------------ | -------------------------------------------------------------------- |
| Schema-Driven Automation       | JSON Schemas define each node’s behavior and structure               |
| Distributed Node Simulation    | Each node runs as a microservice inside its own VM                   |
| Directed Graph-Based Messaging | Communication paths are generated from a graph topology              |
| Query-Based Verification       | SQL queries can be issued to nodes for runtime evaluation            |
| Modular and Extensible         | Add new schemas or modify configurations without changing core logic |
| Monitoring Support (Basic)     | CPU/RAM usage tracking and log output via `psutil` and `nohup`       |

---

## 🔧 Requirements

### Host System

* **OS:** Windows 10/11
* **RAM:** Minimum 8 GB (16 GB recommended)
* **Software:**

  * Oracle VirtualBox
  * Python 3.8+

### Python Dependencies

```bash
pip install paramiko networkx matplotlib requests psutil
```

### VM Requirements

* Debian-based image with:

  * Python 3 + Flask
  * MariaDB
  * SSH access
  * `flask.py` (Flask microservice script)

---

## 📉 Performance & Evaluation

* **Latency:** ∼2.7s–3.3s for SQL queries across nodes
* **Scalability:** Verified up to 6 VMs (urban traffic scenario)
* **Correctness:** 100% functional node deployment in case studies
* **Monitoring:** Resource usage stats logged at each simulation phase

---

## 🤜 Future Enhancements

* Docker-based deployment instead of full VMs
* MQTT or WebSocket-based asynchronous messaging
* Live dashboards using Prometheus + Grafana
* Dynamic behavior scripting with DSLs
* Integration with physical IoT devices (Digital Twin)

---

## 📖 Full Thesis

The complete thesis, including implementation details, case studies, and references is available here:

[**📄 Masterarbeit\_Amin\_Maneshi.pdf**](./Masterarbeit_Amin_Maneshi.pdf)

---

## 📞 Contact

**Amin Maneshi**
Email: [a.maneshi@uni-rostock.de](mailto:a.maneshi@uni-rostock.de)
Faculty of Computer Science and Electrical Engineering
University of Rostock


