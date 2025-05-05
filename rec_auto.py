# flask_server.py
from flask import Flask, request, jsonify
import mysql.connector, json, os
app=Flask(__name__)
DB=os.getenv('DB_NAME','default_db')
# Setup DB
def setup_db():
    try:
        c=mysql.connector.connect(user='root',unix_socket='/var/run/mysqld/mysqld.sock').cursor()
        c.execute(f"CREATE DATABASE IF NOT EXISTS {DB};")
        c.execute(f"GRANT ALL PRIVILEGES ON {DB}.* TO 'sensoruser'@'%' IDENTIFIED BY '';"
                  )
        c.execute("FLUSH PRIVILEGES;")
        c.close()
    except: pass
setup_db()
CFG={'host':'localhost','port':3306,'user':'sensoruser','password':'','database':DB}
# Ensure tables
for tbl in ['sensor_data','edge_data']:
    conn=mysql.connector.connect(**CFG);cur=conn.cursor()
    cur.execute(f"CREATE TABLE IF NOT EXISTS {tbl} (id INT AUTO_INCREMENT PRIMARY KEY,data LONGTEXT,received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
    conn.commit();cur.close();conn.close()

@app.route('/',methods=['GET'])
def idx(): return 'Flask running',200

@app.route('/data',methods=['POST'])
def recv_data():
    d=request.get_json() or {}
    try:
        conn=mysql.connector.connect(**CFG);c=conn.cursor()
        c.execute("INSERT INTO sensor_data(data) VALUES(%s)",(json.dumps(d,separators=(',',':')),))
        conn.commit();c.close();conn.close()
        return jsonify(status='success',message='Sensor stored'),200
    except Exception as e:
        return jsonify(status='error',message=str(e)),500

@app.route('/edge',methods=['POST'])
def recv_edge():
    d=request.get_json() or {}
    try:
        conn=mysql.connector.connect(**CFG);c=conn.cursor()
        c.execute("INSERT INTO edge_data(data) VALUES(%s)",(json.dumps(d,separators=(',',':')),))
        conn.commit();c.close();conn.close()
        return jsonify(status='success',message='Edge stored'),200
    except Exception as e:
        return jsonify(status='error',message=str(e)),500

@app.route('/query',methods=['GET'])
def query():
    try:
        conn=mysql.connector.connect(**CFG);c=conn.cursor()
        c.execute("SELECT COUNT(*) FROM sensor_data WHERE JSON_EXTRACT(data,'$.emergency_cars')='true';")
        cnt=c.fetchone()[0];c.close();conn.close()
        msg='Green light' if cnt>0 else 'Red light'
        return jsonify(status='success',message=msg),200
    except Exception as e:
        return jsonify(status='error',message=str(e)),500

@app.route('/status',methods=['GET'])
def status():
    res=query().get_json(); return f"<h1>{res['message']}</h1>",200

if __name__=='__main__': app.run(host='0.0.0.0',port=5000,debug=True)
