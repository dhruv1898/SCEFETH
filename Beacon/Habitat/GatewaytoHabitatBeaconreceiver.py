import pandas as pd
import socket
import numpy as np
import csv
HOST = '10.10.10.2'
PORT = 50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(10)

while True:
    df = pd.read_csv("Enddeviceroute.csv",sep=' ',header=None)
    df.columns=['Gateway','Enddevice','Rssi']
    #print(df)
    conn, addr = s.accept()
    print('Connected by', addr)
    data = conn.recv(4096).decode()
    data = data.split(':')
    if "ID" in data[0]:
        print(data[0]+':'+data[1])
    else:
        enddevices = data[1].split(';')
        for i in range(0,len(enddevices)):
            if(enddevices[i]!=''):
                enddevices[i] = enddevices[i].replace('[','')
                enddevices[i] = enddevices[i].replace(']','')
                enddevices[i] = enddevices[i].replace('\'','')
                enddevarr = enddevices[i].split(':')
                device = data[0]+' '+enddevices[i]
                if(df["Gateway"].equals(data[0]) & df["Enddevice"].equals(enddevarr[0]))==True:
                    df["Rssi"]=np.where((df["Gateway"]==data[0]) & (df["Enddevice"]==enddevarr[0]), enddevarr[1],df["Rssi"])
                else:
                    df2 = pd.DataFrame({"Gateway":[data[0]],"Enddevice":[enddevarr[0]],"Rssi":[enddevarr[1]]})
                    df=pd.concat([df,df2],ignore_index = True,axis=0)
        df.drop_duplicates(subset=['Gateway','Enddevice'],keep='last', inplace=True)
        #print(df)
        df.to_csv('Enddeviceroute.csv',sep=':',header=False, index=False)
    conn.close()
s.close()