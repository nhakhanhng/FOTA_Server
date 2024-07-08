import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        client.connected_flag = True #set flag
        print("connected OK! Returned code =", rc)
    else:
        print("Bad connection! Returned code =", rc)
    
def on_publish(client, userdata, mid, reason_code, properties):
    print(f'Message ID {mid} with reason code {reason_code}:', end='')

'''
1: MQTT without tls
2: MQTT with tls
3: websockets
'''
using_protocol = 2
if using_protocol == 1:
    server_port = 1883
    protocol = 'tcp'
elif using_protocol == 2:
    server_port = 8883
    protocol = 'tcp'
else:
    server_port = 9001
    protocol = 'websockets'

mqtt.Client.connected_flag=False#create flag in class
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                    protocol=mqtt.MQTTv5,
                    transport=protocol)

client.on_connect = on_connect
client.on_publish = on_publish 

client.username_pw_set("user1", "123456")

if using_protocol == 2:
    client.tls_set(ca_certs="../../certs_keys/ca.crt")

print("Connecting to broker ", end='')
client.connect_async('begvn.home', server_port)      #connect to broker
client.loop_start()
while not client.connected_flag: #wait in loop
    print('... ', end='')
    time.sleep(0.1)

while True:
    pl = int(time.time())
    msg = client.publish(topic='test', payload=pl, qos=2, retain=True)
    msg.wait_for_publish()
    print(pl)
    time.sleep(1)
