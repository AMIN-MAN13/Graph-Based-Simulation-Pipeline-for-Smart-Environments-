# orchestrator.py

import time
import psutil
from statistics import mean
import subprocess
import json
import paramiko
import random
import datetime
import networkx as nx
import matplotlib.pyplot as plt
import requests
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote_plus

VBOXMANAGE = r"C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage.exe"
BASE_VM_NAME = "RPM"
CONFIG_FILE = "config2.json"

# Utility Functions
def run_ssh_command(port, cmd, user="rp", pwd="123", timeout=30):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('localhost', port=port, username=user, password=pwd, timeout=timeout)
    stdin, stdout, stderr = client.exec_command(cmd)
    out, err = stdout.read().decode(), stderr.read().decode()
    client.close()
    if err:
        print(f"SSH stderr[{port}]: {err.strip()}")
    return out.strip()

def wait_for_ssh(port, timeout=300):
    start = time.time()
    while time.time() - start < timeout:
        if run_ssh_command(port, 'echo ok') == 'ok':
            return True
        time.sleep(5)
    print(f"SSH timeout on {port}")
    return False

def wait_for_flask(ip, port=5000, timeout=120):
    url = f"http://{ip}:{port}/"
    start = time.time()
    while time.time() - start < timeout:
        try:
            if requests.get(url, timeout=3).status_code == 200:
                return True
        except:
            pass
        time.sleep(5)
    print(f"Flask not up {ip}:{port}")
    return False

def generate_data_from_schema(schema):
    data = {}
    for key, info in schema.get("properties", {}).items():
        if key in ("$schema", "title"):
            continue
        typ = info.get("type")
        if typ == "boolean":
            data[key] = random.choice([True, False])
        elif typ == "integer":
            data[key] = random.randint(info.get("minimum", 0), info.get("maximum", 100))
        elif typ == "number":
            data[key] = round(random.uniform(info.get("minimum", 0), info.get("maximum", 1000)), 2)
        elif typ == "string":
            data[key] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") if key == "timestamp" else "example"
        else:
            data[key] = None
    return data

# Phase 1: Preparation
def prepare_nodes_and_graph(config_path):
    config = json.load(open(config_path))
    node_data = {}
    for name, meta in config["nodes"].items():
        schema = json.load(open(meta["schema_path"]))
        sim = generate_data_from_schema(schema)
        sim.update({"type": meta["type"], "id": name})
        node_data[name] = sim

    graph = {
        "nodes": list(node_data.values()),
        "edges": config["edges"],
        "generated_at": datetime.datetime.now().isoformat()
    }
    return config, node_data, graph

def draw_networkx_graph(graph):
    G = nx.DiGraph()
    for node in graph["nodes"]:
        G.add_node(node["id"], **node)
    for edge in graph["edges"]:
        et = edge.get("edge_type") or edge.get("type")
        G.add_edge(edge["source"], edge["target"], type=et)
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray')
    labels = {(u, v): d['type'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.savefig("network_graph.png")
    plt.close()
    print("[INFO] Network graph saved to: network_graph.png")

# Phase 2: VM Provisioning
def clone_vm(base, name, port):
    subprocess.run([VBOXMANAGE, "clonevm", base, "--name", name, "--register"], check=True)
    subprocess.run([VBOXMANAGE, "modifyvm", name, "--natpf1", f"guestssh,tcp,,{port},,22"], check=True)
    subprocess.run([VBOXMANAGE, "startvm", name, "--type", "headless"], check=True)
    print(f"Cloned {name}, SSH on port {port}")

def start_flask_server(cfg):
    run_ssh_command(
        cfg['ssh_port'],
        'nohup python3 /home/rp/Desktop/rec_auto.py > flask.log 2>&1 &'
    )

def send_sensor_data(cfg, data):
    try:
        print(requests.post(f"http://{cfg['host']}:5000/data", json=data, timeout=5).json())
    except Exception as e:
        print(f"Data send error: {e}")

def send_edges(config, nodes, cfgs):
    print(f"Sending {len(config['edges'])} edges...")
    for edge in config["edges"]:
        src, tgt = edge["source"], edge["target"]
        payload = {
            "source": nodes[src]["id"],
            "target": nodes[tgt]["id"],
            "edge_type": edge.get("edge_type") or edge.get("type", "default_edge"),
            "data_fields": {f: nodes[src].get(f) for f in edge.get("data_fields", [])}
        }
        cmd = (
            f"curl -s -X POST -H 'Content-Type: application/json' "
            f"-d '{json.dumps(payload)}' "
            f"http://{cfgs[tgt]['host']}:5000/edge"
        )
        print(run_ssh_command(cfgs[src]['ssh_port'], cmd))

# Phase 3: Simulation & Evaluation
def simulate_queries(cfgs, start_total):
    # prompt user for a full SQL statement
    q = input("Enter full SQL to run :\n").strip()
    sql_enc = quote_plus(q)

    latencies = []
    for s in cfgs:
        for t in cfgs:
            if s == t:
                continue
            url = f"http://{cfgs[t]['host']}:5000/query?sql={sql_enc}"
            t0 = time.time()
            raw = run_ssh_command(cfgs[s]['ssh_port'], f"curl -s \"{url}\"")
            latency = time.time() - t0
            latencies.append(latency)

            try:
                resp = json.loads(raw)
                if resp.get("status") == "success":
                    rows = resp.get("rows", [])
                    print(f"[QUERY] {s}→{t}: returned {len(rows)} rows | latency: {latency:.2f}s")
                    # print the full row data:
                    print(json.dumps(rows, indent=2))
                else:
                    print(f"[QUERY] {s}→{t}: ERROR {resp.get('message')} | latency: {latency:.2f}s")
            except Exception:
                print(f"[QUERY ERROR] {s}→{t}: raw={raw[:80]} | latency: {latency:.2f}s")

    print("=" * 40)
    print("PERFORMANCE SUMMARY")
    print("=" * 40)
    print(f"Total time: {time.time() - start_total:.2f}s")
    if latencies:
        print(f"Avg latency: {mean(latencies):.2f}s")
    print(f"CPU: {psutil.cpu_percent()}%  RAM: {psutil.virtual_memory().percent}%")

# Main
if __name__ == '__main__':
    start_total = time.time()
    config, node_data, graph = prepare_nodes_and_graph(CONFIG_FILE)
    print(json.dumps(graph, indent=2))
    draw_networkx_graph(graph)

    ports = [2220 + i for i in range(1, len(node_data) + 1)]
    node_names = list(node_data.keys())

    print("Cloning VMs...")
    with ThreadPoolExecutor(max_workers=len(node_names)) as ex:
        for i, name in enumerate(node_names):
            ex.submit(clone_vm, BASE_VM_NAME, f"{name}_VM", ports[i])

    time.sleep(200)
    for p in ports:
        wait_for_ssh(p)

    print("[WAIT] Sleeping 30 seconds to allow networking to initialize...")
    time.sleep(30)

    print("Getting VM IPs...")
    cfgs = {}
    for i, name in enumerate(node_names):
        port = ports[i]
        ip = None
        retries = 10
        while retries > 0 and not ip:
            out = run_ssh_command(port, "hostname -I").split()
            ip = next((x for x in out if x.startswith("192.168.56.")), None)
            if not ip:
                print(f"[WAIT] IP not ready for {name}. Retrying...")
                time.sleep(5)
                retries -= 1

        if not ip:
            raise RuntimeError(f"Could not get IP for {name} after retries.")
        cfgs[name] = {'host': ip, 'ssh_port': port}

    print("Deploying Flask and sending sensor data...")
    for name in node_names:
        start_flask_server(cfgs[name])
        if not wait_for_flask(cfgs[name]['host']):
            raise RuntimeError(f"Flask failed to start on {name}")

    for name in node_names:
        send_sensor_data(cfgs[name], node_data[name])
    send_edges(config, node_data, cfgs)
    simulate_queries(cfgs, start_total)
