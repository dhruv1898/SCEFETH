import rf95
import time
import pandas as pd
import numpy as np
import socket
import csv

DEBUG= True

# Function to update the Geography table at the Gateway
def storeID(data):
    df = pd.read_csv("Enddeviceroute.csv",sep=':',header=None)
    df.columns=['Enddevice','Rssi']
    data = data.split(':')
    if(df["Enddevice"].equals(data[0]))==True:
        df["Rssi"]=np.where((df["Enddevice"]==data[0]),df["Rssi"])
    else:
        df2 = pd.DataFrame({"Enddevice":[data[0]],"Rssi":[data[1]]})
        df=pd.concat([df,df2],ignore_index = True,axis=0)
    df.drop_duplicates(subset=['Enddevice','Rssi'],keep='last', inplace=True)
    if DEBUG:
        print(df)
    df.to_csv('Enddeviceroute.csv',sep=':',header=False, index=False)

# Function to send message to the Habitat
def sendtohabitat(message):
    HOST = '10.10.10.2'
    PORT = 50007
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST,PORT))
    s.send(message.encode())
    if DEBUG:
        print(message)
    s.close()

# Create rf95 object with CS0 and external interrupt on pin 25, reset pin on 17(BCM pin mapping for RPi)
lora = rf95.RF95(0, 25, 17)

if not lora.init(): # returns True if found
    print("RF95 not found")
    quit(1)
else:
    print("RF95 LoRa mode ok")

# set frequency, power and mode
lora.set_frequency(868.0)
lora.set_tx_power(5)
lora.set_preamble_length(8)
lora.set_modem_config(rf95.Bw125Cr45Sf128)
while True:
    # Wait until data is available
    while not lora.available():
        pass
    # Receive
    data = lora.recv()
    data=data.split(':')

    # RSSI
    rssi = str(lora.rssi())

    # data decode
    data1 = bytes(data[1] +':'+ rssi)
    data2 = data1.decode('utf-8')
    
    #Store ID and RSSI
    storeID(data2)
    
    
    if data[0]=='B':
        if DEBUG:
            print('Beacon Received')
    
    elif data[0]=='D':
        if DEBUG:
            print('Data Received')
        senddata = bytes(data[1]+':'+data[2])
        message = senddata.decode('utf-8')
        sendtohabitat(message)


