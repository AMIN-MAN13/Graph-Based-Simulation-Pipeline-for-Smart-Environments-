# Smart Environment Transformation Pipeline

This repository contains a prototype implementation of an automated transformation pipeline for smart environments. It allows the simulation of distributed sensor networks by converting graph-based specifications into executable runtime nodes deployed on virtual machines.

## Overview

The system uses structured JSON Schema files to define node types and behaviors, then automatically provisions isolated simulation nodes (e.g., as VMs or containers), configures their behavior using Python/Flask, and enables communication between them via HTTP and SQL queries.

This setup is useful for simulating smart city scenarios like urban traffic management, where virtual nodes represent highways, train detectors, and crossroads.

## Included Files

### ✅ `automated.py`

Main entry point for the transformation pipeline. It performs the following:
- Loads node definitions from JSON Schemas
- Validates input node objects
- Generates inter-node communication edges
- Creates internal graph representations for deployment

### ✅ `rec_auto.py`

Deployment automation script responsible for:
- Provisioning virtual machines or services for each node
- Automatically installing required dependencies (e.g., MariaDB)
- Uploading the Flask simulation code
- Starting and monitoring the Flask servers on each VM

### ✅ `type1.json` – **Highway Node Schema**

Defines properties of highway nodes including:
- Vehicle counters in all directions
- Pedestrian sensors
- Emergency vehicle detection
- Turning direction support
- Timestamp formatting

### ✅ `type2.json` – **Train Detector Node Schema**

Defines train detector behavior including:
- Train detection flag (`train_detection`)
- Emergency and pedestrian fields
- Timestamp pattern and vehicle counts

### ✅ `type3.json` – **Small Crossroad Node Schema**

Describes crossroads with environmental monitoring:
- CO₂ level monitoring
- Directional pedestrian and vehicle counters
- Emergency vehicle awareness

## How It Works

1. **Schema Parsing** – Node properties are validated using Python's `jsonschema`.
2. **Edge Generation** – Based on node types, communication edges are created (e.g., train alerts, CO₂ broadcasts).
3. **Code Deployment** – Each node is deployed as a Flask service with a local MariaDB instance.
4. **Data Simulation** – Nodes generate or receive data and communicate via HTTP APIs.

## Features

- 🧩 Modular design for easy extension to new node types
- 🧪 Automatically deploys simulation-ready nodes with full backend
- 🌐 Supports inter-node messaging using REST and SQL
- 🔍 Enables inspection of behavior through logs and queries

## Tech Stack

- Python 3.8+
- Flask (API framework)
- VirtualBox / SSH (deployment)
- MariaDB (local DB per node)
- JSON Schema (input specification)

## Usage

To simulate your own network:
1. Define nodes using JSON Schema
2. Modify or extend `automated.py` to load your schema
3. Run `rec_auto.py` to deploy and simulate

---

