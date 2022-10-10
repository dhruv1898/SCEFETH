# This script is to be used for the Multihop Test.

# This script is to be run on Gateway for:
# 1) sending Data from the End-device to the Habitat.
# 2) sending Gateway's End-device Geography table to the Habitat.
# 3) Time synchronization with Habitat

#Note:
# 1) rf95.py should be kept in the same folder as this script.
# 2) The rf95 library keeps the transceiver in RX mode with the available function.
# 3) The send function puts the transceiver in TX mode.

import rf95
import time
import pandas as pd
import numpy as np
import socket
import csv
from threading import Timer
import os
#import datetime as dt
#from threading import Thread
import ntplib
import sys
#from multiprocessing import Process
import threading

DEBUG = True

Gateway_ID = '10.10.10.4'

correction = 0
timesync_interrupt = time.time()
### function for syncing the clocks of the Gateways with that of Habitat's
def timesync():
    global timesync_interrupt, correction
    try:
        c = ntplib.NTPClient()
        response = c.request('10.10.10.2')
        correction = response.tx_time - time.time()  # response.tx_time is the time of the server
        if DEBUG:
            print('syncing time')
            print(correction)
        #ntplib.ntp_to_system_time(correction)
    except ntplib.NTPException:
        pass
    timesync_interrupt = timesync_interrupt+3600  # 3600 seconds interval
    t1 = Timer(timesync_interrupt - time.time(), timesync)
    t1.start()

timesync()

##########################################################################################

##### This part is for forwarding data from End-device to Habitat ####

# create csv file for Geography table
os.chdir("/root/GATEWAY/")
if os.path.exists("Enddeviceroute.csv"):
    os.remove("Enddeviceroute.csv")
    open("/root/GATEWAY/Enddeviceroute.csv", "w")
else:
    open("/root/GATEWAY/Enddeviceroute.csv", "w")
    if DEBUG:
        print("Created file: Enddeviceroute.csv")

# File ID for storing Test data
last_file_ID = 0
for fn in os.listdir("/root/GATEWAY/"):
    try:
        last_file_ID = max(last_file_ID, int(fn.split('#')[1]))
    except:
        pass
print(f'The old file ID for storing test data was: {last_file_ID}')
new_file_ID = str(last_file_ID + 1)

# for storing E2H test data
if os.path.exists(f"Multihop_data_(@G)_E2H_#{new_file_ID}#.csv"):
    os.remove(f"Multihop_data_(@G)_E2H_#{new_file_ID}#.csv")
    open(f"/root/GATEWAY/Multihop_data_(@G)_E2H_#{new_file_ID}#.csv", "w")
else:
    open(f"/root/GATEWAY/Multihop_data_(@G)_E2H_#{new_file_ID}#.csv", "w")
    if DEBUG:
        print(f"Created file: Multihop_data_(@G)_E2H_#{new_file_ID}#.csv")

filename = "Enddeviceroute.csv" # name of the csv file that stores End-device ID and RSSI

test_result_e2h = f"Multihop_data_(@G)_E2H_#{new_file_ID}#.csv" # name of file that stores the E2H Multihop test data

# Function to store the E2H Multihop test data for data packet
def store_test_data_E2H_B(data):
    for i in range(0, len(test_result_e2h)):
        try:
            df = pd.read_csv(test_result_e2h,sep='/',header=None)
            df.columns=['Date-Time','Type','Enddevice','Rssi','Payload','Packetnumber', 'Direction']
        except:
            column_names = ['Date-Time','Type','Enddevice','Rssi','Payload','Packetnumber', 'Direction']
            df = pd.DataFrame(columns = column_names)
            continue
    
    data = data.split('/')
    df2 = pd.DataFrame({"Date-Time":[data[0]],"Type":[data[1]],"Enddevice":[data[2]],"Rssi":[data[3]],"Payload":np.NaN,"Packetnumber":np.NaN, "Direction":np.NaN})
    df=pd.concat([df,df2],ignore_index = True,axis=0)
    #df.drop_duplicates(subset=['Enddevice'],keep='last', inplace=True)
    #if DEBUG:
        #print(df)
    df.to_csv(test_result_e2h,sep='/',header=False, index=False)

# Function to store the E2H Multihop test data for data packet
def store_test_data_E2H_D(data):
    for i in range(0, len(test_result_e2h)):
        try:
            df = pd.read_csv(test_result_e2h,sep='/',header=None)
            df.columns=['Date-Time','Type','Enddevice','Rssi','Payload','Packetnumber', 'Direction']
        except:
            column_names = ['Date-Time','Type','Enddevice','Rssi','Payload','Packetnumber', 'Direction']
            df = pd.DataFrame(columns = column_names)
            continue
    
    data = data.split('/')
    df2 = pd.DataFrame({"Date-Time":[data[0]],"Type":[data[1]],"Enddevice":[data[2]],"Rssi":[data[3]],"Payload":[data[4]],"Packetnumber":[data[5]], "Direction":[data[6]]})
    df=pd.concat([df,df2],ignore_index = True,axis=0)
    #df.drop_duplicates(subset=['Enddevice'],keep='last', inplace=True)
    #if DEBUG:
        #print(df)
    df.to_csv(test_result_e2h,sep='/',header=False, index=False)

# Function to update the Geography table at the Gateway
def storeID(data):
    for i in range(0, len(filename)):
        try:
            df = pd.read_csv(filename,sep=':',header=None)
            df.columns=['Enddevice','Rssi']
        except:
            column_names = ['Enddevice','Rssi']
            df = pd.DataFrame(columns = column_names)
            continue
    
    data = data.split(':')
    if(df["Enddevice"].equals(data[0]))==True:
        df["Rssi"]=np.where((df["Enddevice"]==data[0]),data[1],df["Rssi"])
    else:
        df2 = pd.DataFrame({"Enddevice":[data[0]],"Rssi":[data[1]]})
        df=pd.concat([df,df2],ignore_index = True,axis=0)
            
    df.drop_duplicates(subset=['Enddevice'],keep='last', inplace=True)
    if DEBUG:
        print(df)
    df.to_csv(filename,sep=':',header=False, index=False)

# Function to send data over Wifi
def send(client, msg):
    HEADER = 64
    FORMAT = 'utf-8'
    message_1 = msg.encode(FORMAT)
    msg_length = len(message_1)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message_1)

# Function to send message to the Habitat
def sendtohabitat(message_2):
    
    HEADER = 64
    HOST = '10.10.10.2' # Habitat's IP
    PORT = 50007  # Port number
    FORMAT = 'utf-8'
    DISCONNECT_MESSAGE = "!!DISCONNECT!!"
    message_2 =message_2.split(':')
    message_3 = message_2[0]+':/'+message_2[1]+':'+message_2[2]
    client_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_1.connect((HOST,PORT))
        send(client_1, message_3)
        datetimestamp_g2h = str(time.time()+correction)
        save_g = datetimestamp_g2h+'/'+'D'+'/'+message_2[0]+'/'+'rssi'+'/'+message_2[1]+'/'+message_2[2]+'/'+'G2H'       
        store_test_data_E2H_D(save_g)
        send(client_1, DISCONNECT_MESSAGE)
        client_1.shutdown(socket.SHUT_RDWR)
        client_1.close()
    except:
        print('running away')
        pass
    
    if DEBUG:
        print(message_2)

# Create rf95 object with CS0 and external interrupt on pin 25, reset pin on 17(BCM pin mapping for RPi)
lora = rf95.RF95(0, 25, 17)

next_interrupt = time.time()

# timer interrupt function to send Gateway's end-device Geography table to Habitat
def timer_function(filename):

    global next_interrupt
    HEADER = 64
    HOST = '10.10.10.2' # Habitat's IP
    PORT = 50007  # Port number
    FORMAT = 'utf-8'
    DISCONNECT_MESSAGE = "!!DISCONNECT!!"
    with threading.Lock():
        client_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_2.connect((HOST,PORT))
            data_string = Gateway_ID+":/"
            with open(filename) as file_obj:
                reader_obj = csv.reader(file_obj)
                for row in reader_obj:
                    data_string = data_string+str(row)+";"
            send(client_2, data_string)
            send(client_2, DISCONNECT_MESSAGE)
            client_2.shutdown(socket.SHUT_RDWR)
            client_2.close()
            if DEBUG:
                print(data_string)
                print("sent the Geography table to Habitat")
        except:
            pass
    
        f = open(filename, "w+")
        f.close()
        next_interrupt = next_interrupt+30  # 30 seconds interval
        t = Timer(next_interrupt - time.time(), timer_function, args=(filename,))
        t.start()

timer_function(filename)

if not lora.init(): # returns True if found
    if DEBUG:
        print("RF95 not found")
    quit(1)
else:
    if DEBUG:
        print("RF95 LoRa mode ok")

# set frequency, power and mode
lora.set_frequency(868.0)
lora.set_tx_power(5)
lora.set_preamble_length(8)
lora.set_modem_config(rf95.Bw125Cr45Sf128)

# proxy thread for parsing LoRa packet
def parse_LoRa_packet(data_recv, lora, recv_time):
    L = ''.join(chr(i) for i in data_recv)
    print(L)
    data = L.split(':')
                
    # RSSI
    rssi = str(lora.rssi())

    try:
        # data arrangement
        data1 = data[1] +':'+ rssi
            
        if data[0]=='B':
            #Store Multihop test data
            datetimestamp = str(time.time()+correction)
            save = datetimestamp+'/'+data[0]+'/'+data[1]+'/'+rssi
            #print(save)
            store_test_data_E2H_B(save)
            #Store ID and RSSI
            storeID(data1)
            if DEBUG:
                print('Beacon Received')
            
        elif data[0]=='D':
            #Store Multihop test date
            datetimestamp_e2h = str(time.time()+correction)
            save = datetimestamp_e2h+'/'+data[0]+'/'+data[1]+'/'+rssi+'/'+data[2]+'/'+data[3]+'/'+'E2G'
            print(save)
            store_test_data_E2H_D(save)
            #Store ID and RSSI
            storeID(data1)
            if DEBUG:
                print('Data Received')
            message_3 = data[1]+':'+data[2]+':'+data[3]
            print(f'data to be sent to habitat on wifi: {message_3}')
            sendtohabitat(message_3)
        elif data[0]=='N':
            #if ((data[1] in assigned_ED) and (Time_sync)):
            response = "N:/"+ Gateway_ID + ":" + str(time.time()+correction+0.020) + ',' + str(recv_time) + ',' + data[2]
            lora.send(lora.str_to_data(response))
            lora.wait_packet_sent()
            s_time = time.time()+correction
            print(f'Time synchronization Packet sent time:  {s_time}')
            
    except IndexError:
        pass
    return

# End-device to Habitat forwarding Main loop
def E2H_forward_main(lora):
    while True:
    # keep transceiver in RX mode
        while not lora.available():
            pass
        # Receive
        # LoRa packet format: for beacon: B:ID
        # LoRa packet format: for data: D:ID:Payload
        # No encoding is used at the End-device
        data_recv = lora.recv()
        #print(data_recv)
        recv_time = time.time() + correction
        parse_LoRa_packet(data_recv, lora, recv_time)
        print(f'[Active Threads]:  {threading.activeCount()}')
        time.sleep(0.01)

E2H_forward_main(lora)