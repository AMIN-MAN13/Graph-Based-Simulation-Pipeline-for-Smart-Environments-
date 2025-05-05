# orchestrator.py
"""
Clone VMs, deploy Flask on each, send sensor data, build and visualize network, send edge messages,
then have each source node query each target's /query endpoint via SSH (which now queries sensor_data).
"""
#!/usr/bin/env python3
import subprocess
import json
import time
import paramiko
import random
import datetime
import networkx as nx
import matplotlib.pyplot as plt
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

VBOXMANAGE = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
edge_rules = {
    "highway":        {"default": {"type": "emergency",    "data_fields": ["emergency_cars"]}},
    "train_detector": {"default": {"type": "train_alert",   "data_fields": ["train_detection"]}},
    "small_crossroad":{"default": [
        {"type": "emergency", "data_fields": ["emergency_cars"]},
        {"type": "CO2",       "data_fields": ["CO2"]}
    ]},
    "default":        {"default": {"type": "default_edge",  "data_fields": []}}
}

def generate_data_from_schema(schema):
    data = {}
    for key, info in schema.get("properties", {}).items():
        if key in ("$schema", "title"): continue
        typ = info.get("type")
        if typ == "boolean": data[key] = random.choice([True, False])
        elif typ == "integer": data[key] = random.randint(info.get("minimum", 0), info.get("maximum", 100))
        elif typ == "number":  data[key] = round(random.uniform(info.get("minimum", 0), info.get("maximum", 1000)), 2)
        elif typ == "string":  data[key] = (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                         if key=="timestamp" else "example")
        else:                   data[key] = None
    return data

# --- VM & SSH utilities ---
def clone_vm(base, name, port):
    try:
        info = subprocess.run([VBOXMANAGE, "showvminfo", base, "--machinereadable"],
                              capture_output=True, text=True, check=True).stdout
        if 'VMState="running"' in info:
            subprocess.run([VBOXMANAGE, "controlvm", base, "poweroff"], check=True)
        subprocess.run([VBOXMANAGE, "clonevm", base, "--name", name, "--register"], check=True)
        subprocess.run([VBOXMANAGE, "modifyvm", name,
                        "--natpf1", f"guestssh,tcp,,{port},,22"], check=True)
        subprocess.run([VBOXMANAGE, "startvm", name, "--type", "headless"], check=True)
        print(f"Cloned {name}, SSH on port {port}")
    except Exception as e:
        print(f"Clone error {name}: {e}")

def run_ssh_command(port, cmd, user="rp", pwd="123", timeout=30):
    client = paramiko.SSHClient(); client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect('localhost', port=port, username=user, password=pwd, timeout=timeout)
        stdin,stdout,stderr = client.exec_command(cmd)
        out,err = stdout.read().decode(), stderr.read().decode()
        client.close()
        if err: print(f"SSH stderr[{port}]: {err.strip()}")
        return out.strip()
    except Exception as e:
        print(f"SSH fail[{port}]: {e}")
        return ""

def wait_for_ssh(port, timeout=300):
    start = time.time()
    while time.time()-start < timeout:
        if run_ssh_command(port, 'echo ok')=='ok': return True
        time.sleep(5)
    print(f"SSH timeout on {port}"); return False

def wait_for_flask(ip, port=5000, timeout=120):
    url=f"http://{ip}:{port}/"
    start=time.time()
    while time.time()-start<timeout:
        try:
            if requests.get(url,timeout=3).status_code==200: return True
        except: pass
        time.sleep(5)
    print(f"Flask not up {ip}:{port}"); return False

# --- Node setup & data posting ---
def start_flask_server(cfg): run_ssh_command(cfg['ssh_port'], 'sudo nohup python3 /home/rp/Desktop/flask_server.py > flask.log 2>&1 &')

def send_sensor_data(cfg, data):
    try: print(requests.post(f"http://{cfg['host']}:5000/data", json=data, timeout=5).json())
    except Exception as e: print(f"Data send error: {e}")

def process_node(key,cfg):
    schema=json.load(open(input(f"Schema path for {key}: ")))
    start_flask_server(cfg)
    sim=generate_data_from_schema(schema)
    sim.update({'ip':cfg['host'],'id':key})
    t=schema.get('title','').lower()
    sim['type']=('highway' if 'highway' in t else 'train_detector' if 'train' in t else 'small_crossroad' if 'small' in t else 'default')
    print(json.dumps(sim,indent=2))
    if wait_for_flask(cfg['host']): send_sensor_data(cfg,sim)
    return sim

# --- Graph functions ---
def build_json_graph(nodes):
    edges=[]
    ks=list(nodes)
    for src in ks:
        for dst in ks:
            if src==dst: continue
            rule=edge_rules.get(nodes[src]['type'],edge_rules['default'])['default']
            for r in (rule if isinstance(rule,list) else [rule]):
                edges.append({'source':nodes[src]['id'],'target':nodes[dst]['id'],'edge_type':r['type'],'data_fields':r['data_fields']})
    return {'nodes':list(nodes.values()),'edges':edges,'generated_at':datetime.datetime.now().isoformat()}

def draw_networkx_graph(nodes):
    G=nx.DiGraph()
    for d in nodes.values(): G.add_node(d['id'],**d)
    for e in build_json_graph(nodes)['edges']:
        G.add_edge(e['source'],e['target'],type=e['edge_type'])
    pos=nx.spring_layout(G)
    nx.draw(G,pos,with_labels=True,node_color='lightblue',edge_color='gray')
    labels={(u,v):d['type'] for u,v,d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)
    plt.show()

# --- Edge sending & query ---
def send_edges_from_node(src,nodes,cfgs):
    cfg=cfgs[src]
    rule=edge_rules.get(nodes[src]['type'],edge_rules['default'])['default']
    for tgt in cfgs:
        if tgt==src: continue
        for r in (rule if isinstance(rule,list) else [rule]):
            payload={'source':nodes[src]['id'],'target':tgt,'edge_type':r['type'],'data_fields':{f:nodes[src].get(f) for f in r['data_fields']}}
            run_ssh_command(cfg['ssh_port'],f"curl -s -X POST -H 'Content-Type: application/json' -d '{json.dumps(payload)}' http://{cfgs[tgt]['host']}:5000/edge")

def instruct_source_to_query_target(src,tgt,cfgs):
    cmd=f"curl -s http://{cfgs[tgt]['host']}:5000/query"
    raw=run_ssh_command(cfgs[src]['ssh_port'],cmd)
    try: return json.loads(raw)
    except: return {'status':'error','message':raw}

# --- Main ---
if __name__=='__main__':
    n=int(input("Number of nodes: "))
    base=input("Base VM name: ")
    ports=[2220+i for i in range(1,n+1)]
    with ThreadPoolExecutor(max_workers=n) as ex:
        for i,p in enumerate(ports,1): ex.submit(clone_vm,base,f"RPi_VM{i}",p)
    time.sleep(200)
    for p in ports: wait_for_ssh(p)
    input("VMs ready? Enter to continue...")
    cfgs={}
    for i,p in enumerate(ports,1):
        out=run_ssh_command(p,r"ip addr show | grep -oP '192\.168\.56\.\d+'")
        ip=out.splitlines()[0] if out else 'NA'
        cfgs[f"Node{i}"]={'host':ip,'ssh_port':p}
    nodes={k:process_node(k,c) for k,c in cfgs.items()}
    print(json.dumps(build_json_graph(nodes),indent=2))
    draw_networkx_graph(nodes)
    for k in cfgs: send_edges_from_node(k,nodes,cfgs)
    for s in cfgs:
        for t in cfgs:
            if s!=t:
                res=instruct_source_to_query_target(s,t,cfgs)
                print(f"{s}→{t}: {res.get('message')}")

