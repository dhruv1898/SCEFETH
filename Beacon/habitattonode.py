import pandas as pd
import socket
from time import sleep
import numpy as np
import csv
PORT = 50001
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.bind((HOST, PORT))
#s.listen(10)
df = pd.read_csv("Enddeviceroute.csv",sep=' ',header=None)
df.columns=['Gateway','Enddevice','Rssi']
while True:
    val = input("Please Enter Enddevice:- ")
    mess= input("Type your message:- ")
    df2 = df.loc[df["Enddevice"]==val]
    print(df2)
    df3 = df2.loc[df2['Rssi']==df2['Rssi'].max()]
    print(df3)
    if df3.shape[0]>1:
        df3.drop_duplicates(subset='Enddevice',keep='first', inplace=True)
    Node = df3.Enddevice.item()
    addr = df3.Gateway.item()
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((addr,PORT))
    data_string = addr+' '+Node+': '+mess
    s.send(data_string.encode())
    print(data_string)
    s.close()
    sleep(15)