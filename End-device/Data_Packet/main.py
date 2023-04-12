#!!! CHANGE ID in 1 place only, at line number 21. !!!#

from time import sleep, ticks_ms, time
#from machine import Pin
# from onewire import DS18X20
# from onewire import OneWires
import socket
from machine import SD
import os
from network import LoRa
import mpy_decimal
import pycom


pycom.heartbeat(False)
offset = 0
Time_sync = False   # Time sync state
DEBUG = True

# Enddevice ID
EnddeviceID = 'ID001'

# DS18B20 data line connected to pin P10
# ow = OneWire(Pin('P10'))
# temp = DS18X20(ow)

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
if DEBUG:
    print("New file id is: "+new_fileid)

file = open("/sd/testdata/datalog_"+new_fileid+"_.csv", "a")

# create LoRa object
lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868)

# initialize LoRa
lora.init(mode = LoRa.LORA, region=LoRa.EU868, frequency = 868000000, tx_power = 14, bandwidth=LoRa.BW_125KHZ, sf=7, preamble=8, coding_rate=LoRa.CODING_4_5, power_mode=LoRa.ALWAYS_ON, tx_iq=False, rx_iq=False,  adr=False, public=False, tx_retries=1, device_class=LoRa.CLASS_C)

# create socket 
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setblocking(False)

c = 0   # packet counter

# function to send data over LoRa
def LoRa_send(data, s):
    global offset
    s.send(data)    
    int_time = mpy_decimal.DecimalNumber(str(ticks_ms())) / mpy_decimal.DecimalNumber(str(1000))
    sleep(0.01)
    sent_time = int_time + offset
    sleep(0.01)
    return sent_time

# Time synchronization function.
def time_sync(s):
    global offset, Time_sync
    
    j = 0
    synchronised = False    

    str_init_time = mpy_decimal.DecimalNumber(str(ticks_ms())) / mpy_decimal.DecimalNumber(str(1000))
    sleep(0.01)
    if DEBUG:
        print("Trying time synchronisation")
    sync_req = str({'Type':'N','ID':EnddeviceID,'init_time':str(str_init_time)})
    if DEBUG:
        print("sync_req:"+sync_req)
    LoRa_send(sync_req, s)    
        
    sync_start = time()
    
    while not synchronised:

        if time() - sync_start >= 3:
            str_init_time = mpy_decimal.DecimalNumber(str(ticks_ms())) / mpy_decimal.DecimalNumber(str(1000))
            sleep(0.01)
            if DEBUG:
                print("Trying time synchronisation")
            sync_req = str({'Type':'N','ID':EnddeviceID,'init_time':str(str_init_time)}) 
            if DEBUG:
                print("sync_req:"+sync_req)
            LoRa_send(sync_req, s)            
            sync_start = time()

        t_data = s.recv(512)               
        t3 = mpy_decimal.DecimalNumber(str(ticks_ms())) / mpy_decimal.DecimalNumber(str(1000))
        sleep(0.01)                      
        if len(t_data)>0:
            if DEBUG:
                print(t_data) 
            L = ''.join(chr(i) for i in t_data)            
            try:
                T_recv = eval(L)
                if T_recv['Type']=='N' and T_recv['ID']==EnddeviceID:                                          
                    t2 = mpy_decimal.DecimalNumber(str(T_recv['Correctiontime']))
                    t1 =  mpy_decimal.DecimalNumber(str(T_recv['recv_time']))
                    t0 =  mpy_decimal.DecimalNumber(str(T_recv['init_time']))                    
                    offset = ((t1-t0) + (t2-t3))/2
                    sleep(0.01)                                      
                    Time_sync = True      
                    if DEBUG:          
                        print('Time synchronised')
                        print('offset is')
                        print(offset)
                    synchronised = True
                    sleep(0.01)
                    pycom.rgbled(0x00ff00) # set RGB to green if time synchronized
            except Exception as e:
                print(e)
                pass
                
time_sync(s)

last_time = 0

while True:
    data = s.recv(512) # Receive    
    sleep(0.05)
    
    if len(data)>0:
        L = ''.join(chr(i) for i in data)        
        
        try:
            data_recv = eval(L)            
        except:
            if DEBUG:
                print("!!! Random packet received, cannot parse. !!!")
        else:
            try:
                if data_recv['ID']==EnddeviceID:
                    if DEBUG:
                        print("data_recv: "+ str(data_recv))
                    pycom.rgbled(0xff0000) # set RGB to red if data is received.                
                    int_time_r = mpy_decimal.DecimalNumber(str(ticks_ms())) / mpy_decimal.DecimalNumber(str(1000))
                    sleep(0.01)
                    time_r = int_time_r + offset
                    sleep(0.01)
                    save_data = {'Time':str(time_r), 'Mode':'H2E'}
                    save_data.update(data_recv)
                    file.write(str(save_data))
                    file.write("\n")
                    file.flush()
                    pycom.rgbled(0x00ff00) # set RGB to green
            except:
                pass

    elif time()-last_time > 30:
        pycom.rgbled(0x0000ff) # set RGB to blue if data is being sent.        
        int_time_s = mpy_decimal.DecimalNumber(str(ticks_ms())) / mpy_decimal.DecimalNumber(str(1000))
        sleep(0.01)
        time_s = int_time_s + offset
        sleep(0.01)
        save_data = {'Time':str(time_s),'Mode':'E2H'}
        data_dict = {'Type':'D','ID':EnddeviceID,'Message':'Payload from '+EnddeviceID,'Packetno.':c}
        save_data.update(data_dict)
        data_send = str(data_dict)
        LoRa_send(data_send, s)        
        file.write(str(save_data))
        file.write("\n")
        file.flush()
        if DEBUG:
            print(data_send)
        c +=1
        last_time = time()
        pycom.rgbled(0x00ff00) # set RGB to green