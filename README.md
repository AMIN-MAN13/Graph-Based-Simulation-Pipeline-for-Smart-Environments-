📡 Graph-Based Simulation Pipeline for Smart Environments
This repository provides the full implementation, configuration, and documentation for the master's thesis:

📘 Title: Transforming Graph Models of Smart Environments for Simulation Purposes
🎓 University: University of Rostock
👨‍💻 Author: Amin Maneshi
📅 Submission Date: 26.05.2025
📄 Thesis PDF: Masterarbeit_Amin_Maneshi.pdf

🔍 Overview
This project introduces a transformation pipeline that automates the deployment of distributed simulations from graph-based models. It simulates smart environments such as urban traffic networks and smart homes using lightweight Flask services, VirtualBox VMs, and schema-driven data generation.

The pipeline supports:

JSON-based system modeling

Automatic schema-driven data generation

Directed graph configuration for inter-node communication

VM provisioning using VirtualBox

REST-based communication via Flask

Node-level local databases using MariaDB

Real-time SQL query execution between nodes

🏗️ System Architecture
The pipeline transforms a high-level graph configuration into a functioning simulation consisting of:

Independently running VMs (1 per node)

Flask-based APIs simulating sensor behavior

Inter-node HTTP messaging based on graph edges

Local MariaDB storage per node

SQL-based behavior validation across the system

The process is fully automated through Python scripts and configuration files.

📂 Repository Structure
pgsql
Copy
Edit
├── main.py                         # Main orchestration script
├── Masterarbeit_Amin_Maneshi.pdf  # Final PDF of the thesis
├── network_config.json            # Graph topology for simulation
├── config2.json                   # Alternative simulation configuration
├── type1.json / type2.json / type3.json
│                                  # Schemas for traffic simulation node types
├── kitchen_schema.json
├── livingroom_schema.json
├── kidsroom_schema.json
├── masterbedroom_schema.json     # Schemas for smart home simulation
├── 12.json / 13.json              # Sample data files used in simulation
🚀 How It Works
Define Topology:

Use network_config.json to define nodes and edges.

Each node links to a schema file (e.g., kitchen_schema.json) describing its sensor fields.

Configure Simulation:

The main.py script reads JSON config and builds the simulation graph.

Provision VMs:

Each node is cloned into its own VirtualBox VM.

Flask and MariaDB are launched on each VM via SSH using Paramiko.

Simulate Behavior:

Sensor and edge data is generated based on schema definitions.

Nodes send/receive data through HTTP and store it in their local database.

Query Behavior:

Arbitrary SQL queries can be executed across nodes via /query endpoint for evaluation and verification.

📊 Use Cases Demonstrated
Two scenarios were used to test and evaluate the system:

1. 🛣️ Urban Traffic Management
Simulates train alerts, emergency routing, and CO2 broadcasting between city nodes.

2. 🏠 Smart Home Environment
Models inter-room communication based on sensor data such as motion, gas leak, humidity, and brightness.

✅ Features
Schema-driven automation

Modular and extensible architecture

Node-level query execution

Dynamic schema evolution

Visualization of network topology

Real-time monitoring and logging

🧪 Requirements
Host OS: Windows 10/11 (for VirtualBox and SSH scripts)

Python: 3.8+

Libraries: paramiko, networkx, matplotlib, psutil, requests

VirtualBox: with a base Debian VM (pre-configured)

MariaDB and Flask installed in the base VM

🔧 Setup Instructions
Clone the repository:

bash
Copy
Edit
git clone https://github.com/AMIN-MAN13/Graph-Based-Simulation-Pipeline-for-Smart-Environments-.git
cd Graph-Based-Simulation-Pipeline-for-Smart-Environments-
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Ensure you have:

VirtualBox with a base VM configured

JSON schemas and config files adjusted for your test

SSH keys or password set for VM access (e.g., user rp)

Run the simulation:

bash
Copy
Edit
python main.py
📘 Thesis Reference
The full methodology, design decisions, evaluations, and results are explained in the thesis document:

📄 Masterarbeit_Amin_Maneshi.pdf

🧠 Future Work
Replace VMs with Docker for scalability

Integrate MQTT/WebSockets for real-time communication

Add Prometheus + Grafana for live monitoring

Enable dynamic behavior scripting using DSL

Extend to support real sensor hardware (Digital Twins)

📬 Contact
Author: Amin Maneshi
Email: a.maneshi@uni-rostock.de
University: University of Rostock – Faculty of Computer Science and Electrical Engineering

