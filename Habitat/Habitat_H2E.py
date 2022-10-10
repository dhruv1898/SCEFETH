import pandas as pd
import socket
import os
import time

DEBUG = True

# File ID for storing Test data
last_file_ID = 0
for fn in os.listdir("/root/HABITAT/"):
    try:
        last_file_ID = max(last_file_ID, int(fn.split('#')[1]))
    except:
        pass
print(f'The old file ID for storing test data was: {last_file_ID}')
new_file_ID = str(last_file_ID + 1)

if os.path.exists(f"Multihop_data_(@H)_H2E_#{new_file_ID}#.csv"):
    os.remove(f"Multihop_data_(@H)_H2E_#{new_file_ID}#.csv")
    open(f"/root/HABITAT/Multihop_data_(@H)_H2E_#{new_file_ID}#.csv", "w")
else:
    open(f"/root/HABITAT/Multihop_data_(@H)_H2E_#{new_file_ID}#.csv", "w")
    if DEBUG:
        print(f"Created file: Multihop_data_(@H)_H2E_#{new_file_ID}#.csv")

test_result_h2e = f"Multihop_data_(@H)_H2E_#{new_file_ID}#.csv" # name of file that stores the Multihop test data

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

# Function to store the Multihop test data for data packet
def store_test_data_h2e(data):
    for i in range(0, len(test_result_h2e)):
        try:
            df = pd.read_csv(test_result_h2e,sep='/',header=None)
            df.columns=['Date-Time','Gateway','Enddevice','Payload','Packetnumber']
        except:
            column_names = ['Date-Time','Gateway','Enddevice','Payload','Packetnumber']
            df = pd.DataFrame(columns = column_names)
            continue
    
    data = data.split('/')
    df2 = pd.DataFrame({"Date-Time":[data[0]],"Gateway":[data[1]],"Enddevice":[data[2]],"Payload":[data[3]],"Packetnumber":[data[4]]})
    df=pd.concat([df,df2],ignore_index = True,axis=0)
    #df.drop_duplicates(subset=['Enddevice'],keep='last', inplace=True)
    #if DEBUG:
        #print(df)
    df.to_csv(test_result_h2e,sep='/',header=False, index=False)

h2epacketnumber = 0
HEADER = 64
hostname = '10.10.10.2'
PORT = 50001
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!!DISCONNECT!!"
while True:
    time.sleep(40)
        
    #try:
    print('Im trying') 
    
    #Reading Geography Table
    try:
        df = pd.read_csv("Enddeviceroute.csv",sep=':',header=None)
        df.columns=['Gateway','Enddevice','Rssi']
    except:  
        column_names = ['Gateway','Enddevice','Rssi']
        df = pd.DataFrame(columns = column_names)
        continue

    #Sorting values based on Enddevice and RSSI
    df = df.sort_values(by=['Enddevice','Rssi'],ascending=False)
    #Drop duplicat Enddevices           
    df2 = df.drop_duplicates(subset=['Enddevice'],keep='first')
    print('reached here')
    #Reset index
    df2 = df2.reset_index()
    mess= "Greetings from Habitat!"
    print(mess)
    #Loop to iterate over the Enddevices
    for idx, row in df2.iterrows():
        Enddeviceid = row['Enddevice']
    
        idex=[]
        idex = df.index[df['Enddevice']==Enddeviceid]
        if len(idex)>0:
            #Dataframe for the matching enddevice
            df3 = df.loc[df["Enddevice"]==Enddeviceid]
            df3.sort_values(by="Rssi",ascending=False,ignore_index=True)
            if df3.shape[0]>0:
                sent = False
                #Iterate over same Enddevice connected with multiple gateways
                for ind in df3.index:
                    print(ind)
                    df4=df3.loc[ind]
                    Node = df4.Enddevice
                    addr = df4.Gateway
                    if sent == False:
                        try:
                            client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                            client.connect((addr,PORT))
                            data_string = hostname+':/'+Node+':'+mess+':' + str(h2epacketnumber)
                            send(client, data_string)
                            send(client, DISCONNECT_MESSAGE)
                            datetimestamp = str(time.time())
                            print(data_string)
                            save = datetimestamp + '/' + addr + '/' + Node + '/' + mess+'/'+str(h2epacketnumber)
                            store_test_data_h2e(save)
                            client.shutdown(socket.SHUT_RDWR)
                            client.close()
                            print(f"sent the message to {Node} through Gateway: {addr}")
                            sent = True
                        except:
                            print("[ERROR]")
                            pass               
        else:
            print("ID not found! Please try a different ID :D")
        time.sleep(5)
        #except:
            #print('Empty Table')
            #pass
    h2epacketnumber +=1
    time.sleep(30)