import paho.mqtt.client as mqtt
from Security import Security
import ssl
import os
import io
import re
import threading


host = 'begvn.home'
port = 8883
ca_cert_path = './certs/ca.crt'
Upload_Topic ='SWUpload'
JetSON_MasterApp_Topic = 'SW/Jetson/FOTA_Master_App'
JetSON_MasterBoot_Topic = 'SW/Jetson/FOTA_Master_Boot'
JetSON_Client_Topic = 'SW/Jetson/FOTA_Client'
Jetson_Topic = [JetSON_MasterApp_Topic,JetSON_MasterBoot_Topic,JetSON_Client_Topic]
SW_Types = ['FOTA_Master_App','FOTA_Master_Boot','FOTA_Client']

def MQTT_On_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        client.connected_flag = True #set flag
        print("connected OK! Returned code =", rc)
    else:
        print("Bad connection! Returned code =", rc)
        
def NextVersion_SW(SWname):
    CurrentSWname = GetCurrentSWName(SWname)
    match = re.match(r"(.*)(_v(\d+))(\.py)?$",CurrentSWname)
    # print("Version")
    # print(match.group(1), match.group(3))
    SWType = match.group(1)
    SWversion = match.group(3)
    NextSWVersion = int(SWversion) + 1
    NextSWname = f'{SWType}_v{NextSWVersion}'
    DeleteSW(CurrentSWname)
    return NextSWname
        
def GetCurrentSWName(SWType):
    SWs = os.listdir('../FTP/server/SW')
    for SW in SWs:
        if SW.find(SWType) != -1:
            return SW
    return SWType + '_v0'
        
def DeleteSW(SWname):
    SWpath = os.path.join('../FTP/server/SW',SWname)
    print("Path: ",SWpath)
    if os.path.exists(SWpath):
        os.remove(SWpath)

def MQTT_Publish_SW_Info(MQTTClient,SWname):
    match = re.match(r"(.*)(_v(\d+))(\.py)?$",SWname)
    print(match.group(1), match.group(3))
    SWType = match.group(1)
    for index,SW_Type in enumerate(SW_Types):
        if SW_Type == SWType:
            MQTTClient.publish(Jetson_Topic[index],SWname,retain=True) 
        

def SW_Proccess_Thread(MQTTClient,SWname):
    try:
        Unverified_SWpath = os.path.join('../FTP/server/Unverified_SW',SWname)
        with open(Unverified_SWpath,'rb') as file:
            Unverified_SW = file.read()
        Verified_SW =  Security.Verify_Decrypt(Unverified_SW)
        if (Verified_SW != None):
            print("Verify Successful!")
            NextSWName = NextVersion_SW(SWname)
            Verified_SWpath = os.path.join('../FTP/server/SW',NextSWName)
            MQTTClient.publish(Upload_Topic,"Done")
            MQTT_Publish_SW_Info(MQTTClient,NextSWName)
            with open(Verified_SWpath,'wb') as file:
                file.write(Unverified_SW)
        else:
            print("Sw verify failed!")
            MQTTClient.publish(Upload_Topic,"Fail")
        # os.remove(Unverified_SWpath)
    except Exception as e:
        MQTTClient.publish(Upload_Topic,"Fail")
        print(f'Error occured: {e}')
    
    

def MQTT_On_message(client, userdata, message):
    payload = message.payload.decode()
    topic = message.topic
    if payload == 'FOTA_Master_App' or payload == 'FOTA_Master_Boot' or payload == 'FOTA_Client':
        Proccess_thr = threading.Thread(target=SW_Proccess_Thread,args=(client,payload,))
        Proccess_thr.start()
        
        
if __name__ == "__main__":
    MQTTClient = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                protocol=mqtt.MQTTv5,
                transport='tcp')
    MQTTClient.tls_set(ca_certs=ca_cert_path)
    MQTTClient.on_message = MQTT_On_message
    MQTTClient.username_pw_set("user1", "123456")
    MQTTClient.on_connect = MQTT_On_connect
    MQTTClient.connect(host,port)
    print("Connecting")
    MQTTClient.subscribe(Upload_Topic,qos=2)
    # MQTTClient.publish(Upload_Topic,"Done")
    # Version_SW("FOTA_Master_App_v1")
    MQTTClient.loop_forever()
    