import mysql.connector
import time
import json
import paho.mqtt.client as mqtt

payload = dict()

def on_connect(client, userdata, flags, rc):
    print(f"CONSUME: Connected with result code {rc}")
    # client.subscribe('#') # for all topics
    client.subscribe(topic) # for one topic
    
def on_message(client, userdata, msg):
    try:
        global payload
        payload = json.loads(msg.payload)
        # print(f"Received data from {msg.topic}: {payload}")
        # client.loop_stop()
    except json.JSONDecodeError:
        print(f"Received data from {msg.topic} but failed to decode JSON")
        # client.loop_stop()

with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)
    
db_config = config_data['mysql']
mqtt_broker = config_data['Messenger']
persistent_data = config_data.get('persistent_data', False)

print("Loaded settings...")
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

client = mqtt.Client()

address = mqtt_broker["address"]
port = mqtt_broker["port"]
keepalive = mqtt_broker["keepalive"]
topic = mqtt_broker["topic"]

client.connect(address, port, keepalive)
# client.connect('10.1.103.23', 1883, 60)

# client.loop_start()
# client.loop_forever()

if not persistent_data:
    cursor.execute("DROP TABLE IF EXISTS test_data")
    print("Dropped table due to persistent_data disabled")
    conn.commit()

create_table_query = """
CREATE TABLE IF NOT EXISTS test_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    x VARCHAR(255) NOT NULL,
    value VARCHAR(255) NOT NULL
)
"""

cursor.execute(create_table_query)
conn.commit()

client.on_connect = on_connect
client.on_message = on_message

print("Now waiting for numbers...")

client.loop_start()

try:
    while True:
        if payload:
            insert_data_query = "INSERT INTO test_data (x,value) VALUES ('{}','{}')".format(next(iter(payload)),payload["value"])
            cursor.execute(insert_data_query)
            conn.commit()
            print(f"Inserted {payload}")
            payload = dict()
except KeyboardInterrupt:
    print("Stopping the script!")

cursor.close()
conn.close()