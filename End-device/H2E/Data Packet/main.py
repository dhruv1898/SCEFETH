# change ID in 3 places.

import time
#from machine import Pin
#from onewire import DS18X20
#from onewire import OneWire
import socket
from machine import SD
import os
from network import LoRa
#import _thread
#import utime
#from machine import Timer
import mpy_decimal
import pycom
pycom.heartbeat(False)

correction = 0

Time_sync = False   # Time sync state

sync_period = 10

#LoRa_Device_ID = b'10'

#lock = _thread.allocate_lock()

# DS18B20 data line connected to pin P10
#ow = OneWire(Pin('P10'))
#temp = DS18X20(ow)

# create SD object
sd = SD()
sd.init()
os.mount(sd, '/sd')

# create files to store Enddevice data
os.chdir("/sd/testdata")
last_fileid = 0
for fn in os.listdir('/sd/testdata'):
    try:
        last_fileid = max(last_fileid, int(fn.split('_')[1]))
    except:
        pass

new_fileid= str(last_fileid + 1)
print(new_fileid)

file = open("/sd/testdata/datalog_"+new_fileid+"_.csv", "a")

# create LoRa object
lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868)

# initialize LoRa
lora.init(mode = LoRa.LORA, region=LoRa.EU868, frequency = 868000000, tx_power = 2, bandwidth=LoRa.BW_125KHZ, sf=7, preamble=8, coding_rate=LoRa.CODING_4_5, power_mode=LoRa.ALWAYS_ON, tx_iq=False, rx_iq=False, adr=False, public=False, tx_retries=1, device_class=LoRa.CLASS_C)

# create socket 
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setblocking(False)

c = 0   # packet counter
i = 0

# function to send data over LoRa
def LoRa_send(data, s):
    global correction
    s.send(data)
    sent_time = mpy_decimal.DecimalNumber(time.time()) + correction
    return sent_time

# function to receive data over LoRa
def LoRa_recv(s):
    global correction
    data = s.recv(2048)
    L = ''.join(chr(i) for i in data)
    received_time = mpy_decimal.DecimalNumber(time.time()) + correction    
    return L, received_time

# Time sync
def time_sync(s):
    global offset, Time_sync
    #with lock:
    j = 0
    synchronised = False
    #str(utime.localtime(utime.time(+offset)))
    print("Trying time synchronisation")
    sync_req = 'N:ID003:'+str(time.time())
    print(sync_req)
    LoRa_send(sync_req, s)        
    #Recv = LoRa_recv(s)
    #print(Recv)
    while not synchronised:
        if j>5:
            LoRa_send(sync_req, s)
            print("Trying time synchronisation")
            j = 0
        data = s.recv(256)
        #L = ''.join(chr(i) for i in data)
        t3 = mpy_decimal.DecimalNumber(time.time())
        #t3 = Recv[1]
        #T_recv = L
        print(data)
        j += 1
        time.sleep(0.5)
        if len(data)>0:
            L = ''.join(chr(i) for i in data)
            T_recv = L.split(':')
            if T_recv[0]=='N':
                t = T_recv[2].split(',')
                t2 = mpy_decimal.DecimalNumber(t[0])
                t1 =  mpy_decimal.DecimalNumber(t[1])
                t0 =  mpy_decimal.DecimalNumber(t[2])
                offset = ((t1-t0) + (t2-t3))/2
                #offset = t3 + offset
                Time_sync = True
                #sync_period = 3600
                print('Time synchronised')
                print('offset is')
                print(offset)
                synchronised = True
#j = 0                
#while (j<2):
    #time_sync(s)
    #time.sleep(3)
    #print(j)
    #j += 1
#timer = Timer.Alarm(time_sync, sync_period, arg=s,periodic=True)
time_sync(s)

def data_send(file, temp):
    global c,i
    while True:
        if i == 30:
            taapman = 100/100
            #temp.start_conversion()
            data_send = 'D:ID003: Moin! Temperature value =  ' + str(taapman) + ':' + str(c) # packet format
            LoRa_send(data_send, s)
            file.write(str(mpy_decimal.DecimalNumber(time.time())+offset)+':'+'E2H'+': '+data_send)   # put 15 because time offset observed, correct later.
            file.write("\n")
            file.flush()
            print(data_send)
            c +=1
            i = 0
        time.sleep(1)
        i +=1

def recv_data(s, file):
    
    #while True:
    pycom.rgbled(0xff00)
    #print("Reached here 1")      
    data = s.recv(256) # Receive
    #print("Reached here 2")
    L = ''.join(chr(i) for i in data)
    #print("Reached here 3")
    data = L
    #t_save = data_re[1] + correction
    data_receive1 = data.split(':/')
    time.sleep(0.05)
    #print("REached here 4")
    if data_receive1[0]=='ID003':
        print(data_receive1[1])
        pycom.rgbled(0x7f7f00)
        #data_receive = data_receive.split(':/')
        file.write(str(mpy_decimal.DecimalNumber(time.time())+offset)+':'+'H2E'+':'+data_receive1[0]+':'+data_receive1[1])
        file.write("\n")
        file.flush()
        time.sleep(1)
        
while True:
    if Time_sync:
        #_thread.start_new_thread(data_send, (file, temp))
        #_thread.start_new_thread(recv_data, (s, file))
        #break
        recv_data(s, file)