# This script is to be run on Habitat for:
# 1) receiving Data from the End-device forwarded by the Gateway.

import pandas as pd
import socket
import os
import time

DEBUG = True

os.chdir("/root/HABITAT/")
if os.path.exists("Enddeviceroute.csv"):
    os.remove("Enddeviceroute.csv")
    open("/root/HABITAT/Enddeviceroute.csv", "w")
else:
    open("/root/HABITAT/Enddeviceroute.csv", "w")
    if DEBUG:
        print("Created file: Enddeviceroute.csv")

# File ID for storing Test data
last_file_ID = 0
for fn in os.listdir("/root/HABITAT/"):
    try:
        last_file_ID = max(last_file_ID, int(fn.split('#')[1]))
    except:
        pass
print(f'The old file ID for storing test data was: {last_file_ID}')
new_file_ID = str(last_file_ID + 1)

if os.path.exists(f"Multihop_data_(@H)_E2H_#{new_file_ID}#.csv"):
    os.remove(f"Multihop_data_(@H)_E2H_#{new_file_ID}#.csv")
    open(f"/root/HABITAT/Multihop_data_(@H)_E2H_#{new_file_ID}#.csv", "w")
else:
    open(f"/root/HABITAT/Multihop_data_(@H)_E2H_#{new_file_ID}#.csv", "w")
    if DEBUG:
        print(f"Created file: Multihop_data_(@H)_E2H_#{new_file_ID}#.csv")

filename = "Enddeviceroute.csv" # name of the csv file that stores End-device ID and RSSI

test_result_e2h = f"Multihop_data_(@H)_E2H_#{new_file_ID}#.csv" # name of file that stores the Multihop test data

# Function to store the E2H Multihop test data for data packet
def store_test_data_e2h(data):
    for i in range(0, len(test_result_e2h)):
        try:
            df = pd.read_csv(test_result_e2h,sep='/',header=None)
            df.columns=['Date-Time','Gateway','Gateway_Port','Enddevice','Payload','Packetnumber']
        except:
            column_names = ['Date-Time','Gateway','Gateway_Port','Enddevice','Payload','Packetnumber']
            df = pd.DataFrame(columns = column_names)
            continue
    
    data = data.split('/')
    print(data)
    df2 = pd.DataFrame({"Date-Time":[data[0]],"Gateway":[data[1]], "Gateway_Port": [data[2]],"Enddevice":[data[3]],"Payload":[data[4]],"Packetnumber":[data[5]]})
    df=pd.concat([df,df2],ignore_index = True,axis=0)
    #df.drop_duplicates(subset=['Enddevice'],keep='last', inplace=True)
    #if DEBUG:
        #print(df)
    df.to_csv(test_result_e2h,sep='/',header=False, index=False)

# save data function
def saving(data, filename, addr):
    print(data)
    
    for i in range(0, len(filename)):
        try:
            df = pd.read_csv(filename, sep=':', header=None)
            df.columns=['Gateway','Enddevice','Rssi']
        except:
            column_names = ['Gateway','Enddevice','Rssi']
            df = pd.DataFrame(columns = column_names)
            continue
    datetimestamp = str(time.time())    
    data = data.split(':/')
    if "ID" in data[0]:
        print(data[0]+':'+data[1])
        data_s = data[1].split(':')
        save_D = datetimestamp + '/' + addr[0] + '/' + str(addr[1]) + '/' + data[0] + '/' + data_s[0] + '/' + data_s[1]
        store_test_data_e2h(save_D)
    else:
        try:
            enddevices = data[1].split(';')
            print('Connected by', addr)
            idx=df.index[df['Gateway']==data[0]]
            df.drop(idx,inplace=True)
            for i in range(0,len(enddevices)):
                if(enddevices[i]!=''):
                    enddevices[i] = enddevices[i].replace('[','')
                    enddevices[i] = enddevices[i].replace(']','')
                    enddevices[i] = enddevices[i].replace('\'','')
                    enddevarr = enddevices[i].split(':')
                    df2 = pd.DataFrame({"Gateway":[data[0]],"Enddevice":[enddevarr[0]],"Rssi":[enddevarr[1]]})
                    save_B = datetimestamp + '/' + addr[0] + '/' + str(addr[1]) + '/' + enddevarr[0] + '/' + "NaN"+ '/' + "NaN"
                    store_test_data_e2h(save_B)
                    df=pd.concat([df,df2],ignore_index = True,axis=0)
            df.drop_duplicates(subset=['Gateway','Enddevice'],keep='last', inplace=True)
            if DEBUG:
                print(df)
            df.to_csv('Enddeviceroute.csv',sep=':',header=False, index=False)
        except:
            pass
    
    return

# Function to send data over Wifi
def send(client, msg):
    HEADER = 64
    FORMAT = 'utf-8'
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

HEADER = 64
HOST = '10.10.10.2'
PORT = 50007
addr1 = (HOST, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!!DISCONNECT!!"

# create server with addr
s = socket.create_server(addr1, family = socket.AF_INET, backlog = 5, reuse_port = True, dualstack_ipv6 = False)
#s.bind(addr1)

# Data format which Gateway receives from Habitat IP:/['ID:RSSI'];['ID:RSSI'];....so on
# IP = Gateway's IP address
# ID = End-device ID
# RSSI = Rssi received by Gateway from the End-device

# Handle a Gateway client
def handle_Gateway(conn, addr):
    print(f"[NEW GATEWAY CONNECTION] {addr} connected.")
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            print(msg_length)
            msg_length = int(msg_length)
            data = conn.recv(msg_length).decode(FORMAT)
            print(f"[{addr}] {data}")
            if data == DISCONNECT_MESSAGE:
                break
            saving(data, filename, addr)
            #saving(data, filename, addr)
            #if data == DISCONNECT_MESSAGE:
                #connected = False
            #print(f"[{addr}] {data}")
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()
    
print("[STARTING] Habitat is starting...")
s.listen(5)
print(f"[LISTENING] Habitat is listening on {HOST}")
while True:
    conn, addr = s.accept()
    handle_Gateway(conn, addr)
    time.sleep(0.001)