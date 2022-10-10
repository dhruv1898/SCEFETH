# This script is to be used for the Multihop Test.

# This script is to be run on Gateway for:
# 1) receiving Data from Habitat and,
# 2) forwarding the Data to the respective End-device
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
from threading import Thread
import ntplib
import sys
#from multiprocessing import Process
import threading

DEBUG = True

Gateway_ID = '10.10.10.7'

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

# File ID for storing Test data
last_file_ID = 0
for fn in os.listdir("/root/GATEWAY/"):
    try:
        last_file_ID = max(last_file_ID, int(fn.split('#')[1]))
    except:
        pass
print(f'The old file ID for storing test data was: {last_file_ID}')
new_file_ID = str(last_file_ID + 1)

# for storing H2E test data
if os.path.exists(f"Multihop_data_(@G)_H2E_#{new_file_ID}.#csv"):
    os.remove(f"Multihop_data_(@G)_H2E_#{new_file_ID}#.csv")
    open(f"/root/GATEWAY/Multihop_data_(@G)_H2E_#{new_file_ID}#.csv", "w")
else:
    open(f"/root/GATEWAY/Multihop_data_(@G)_H2E_#{new_file_ID}#.csv", "w")
    if DEBUG:
        print(f"Created file: Multihop_data_(@G)_H2E_#{new_file_ID}#.csv")

test_result_h2e = f"Multihop_data_(@G)_H2E_#{new_file_ID}#.csv" # name of file that stores the H2E Multihop test data

# Function to store the H2E Multihop test data for data packet
def store_test_data_H2E(data):
    for i in range(0, len(test_result_h2e)):
        try:
            df = pd.read_csv(test_result_h2e,sep='/',header=None)
            df.columns=['Date-Time','Habitat','Enddevice','Payload']
        except:
            column_names = ['Date-Time','Habitat','Enddevice','Payload']
            df = pd.DataFrame(columns = column_names)
            continue
    
    data = data.split('/')
    df2 = pd.DataFrame({"Date-Time":[data[0]],"Habitat":[data[1]],"Enddevice":[data[2]],"Payload":[data[3]]})
    df=pd.concat([df,df2],ignore_index = True,axis=0)
    #df.drop_duplicates(subset=['Enddevice'],keep='last', inplace=True)
    #if DEBUG:
        #print(df)
    df.to_csv(test_result_h2e,sep='/',header=False, index=False)

# Create rf95 object with CS0 and external interrupt on pin 25, reset pin on 17(BCM pin mapping for RPi)
lora = rf95.RF95(0, 25, 17)
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

#### This part is for forwarding data from Habitat to End-device ####

# proxy thread for parsing LoRa packet
def parse_LoRa_packet(data_recv, lora, recv_time):
    L = ''.join(chr(i) for i in data_recv)
    print(L)
    data = L.split(':')
   
    try:
        # data arrangement              
        if data[0]=='N':
            #if ((data[1] in assigned_ED) and (Time_sync)):
            response = "N:/"+ Gateway_ID + ":" + str(time.time()+correction+0.020) + ',' + str(recv_time) + ',' + data[2]
            lora.send(lora.str_to_data(response))
            lora.wait_packet_sent()
            s_time = time.time()+correction
            print(f'Time synchronization Packet sent time:  {s_time}')
            
    except IndexError:
        pass
    return

# function to send data to the End-device
def toenddevice(message, lora):
    message_1 = message.split(':/')
    print(message_1)
    enddev = message_1[1].split(':')
    print(enddev)
    sendmessage = enddev[0]+':/'+message_1[0]+':'+enddev[1] + ':' + enddev[2]
    # Store H2E Multihop test data
    datetimestamp_h2e = str(time.time()+correction)
    save = datetimestamp_h2e + '/' + enddev[0] + '/' + message_1[0] + '/' + enddev[1] + '/' + enddev[2]
    store_test_data_H2E(save)
    if DEBUG:
        print('Stored H2E Multihop test data')
    # Send some data
    lora.send(lora.str_to_data(sendmessage))
    lora.wait_packet_sent()
    if DEBUG:
        print(sendmessage)
    time.sleep(0.1)

# Packet format which Gateway receives from Habitat IP:/ID:Payload
# IP = Habitat's IP address
# ID = End-device ID
# Payload = Payload data

# Packet format which Gateway sends to the End-device ID:/IP:Payload
# ID = End-device ID
# IP = Habitat's IP address
# Payload = Payload data

# Handle H2E connection
def handle_Habitat(conn, addr, lora):

    HEADER = 64
    FORMAT = 'utf-8'
    DISCONNECT_MESSAGE = "!!DISCONNECT!!"
    
    print(f"[HABITAT CONNECTION] {addr} connected.")
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            data = conn.recv(msg_length).decode(FORMAT)
            print(f"[{addr}] {data}")
            if data == DISCONNECT_MESSAGE:
                break
            toenddevice(data, lora)
            #if data == DISCONNECT_MESSAGE:
                #connected = False
                
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()

# Habitat to End-device forwarding Main loop
def H2E_forward_main(lora):

    HEADER = 64
    HOST=Gateway_ID #change IP address for each Gateway here
    PORT=50001
    addr = (Gateway_ID, 50001)
    FORMAT = 'utf-8'
    DISCONNECT_MESSAGE = "!!DISCONNECT!!"

    # create server with addr
    #G_server = socket.create_server(addr, family = socket.AF_INET, backlog = 5, reuse_port = True, dualstack_ipv6 = False)
    #G_server.bind(addr)
    #G_server.listen(5)

    while True:
        while not lora.available():
            pass
        # Receive
        # LoRa packet format: for beacon: B:ID
        # LoRa packet format: for data: D:ID:Payload
        # No encoding is used at the End-device
        data_recv = lora.recv()
        print(data_recv)
        recv_time = time.time() + correction
        parse_LoRa_packet(data_recv, lora, recv_time)
        print(f'[Active Threads]:  {threading.activeCount()}')
        time.sleep(0.01)
        #conn,addr = G_server.accept()
        #handle_Habitat(conn, addr, lora)
        #print(f'[Active Threads]:  {threading.activeCount()}')
        #thread_3 = Thread(target = handle_Habitat, args=(conn, addr, lora,))
        #thread_3.daemon = True
        #thread_3.start()
        #print(f'[Active Threads]:  {threading.activeCount()}')
        #time.sleep(0.001)

H2E_forward_main(lora)