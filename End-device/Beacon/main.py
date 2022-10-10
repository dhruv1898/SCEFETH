from network import LoRa
import time
import socket

# create LoRa object
lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868)

# initialize LoRa
lora.init(mode = LoRa.LORA, region=LoRa.EU868, frequency = 868000000, tx_power = 2, bandwidth=LoRa.BW_125KHZ, sf=7, preamble=8, coding_rate=LoRa.CODING_4_5, power_mode=LoRa.ALWAYS_ON, tx_iq=False, rx_iq=False, adr=False, public=False, tx_retries=1, device_class=LoRa.CLASS_C)

# create socket 
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setblocking(False)

i = 0

while True:
    if i ==5:
        data_send = 'B:ID002'
        s.send(data_send) # Send
        print(data_send)
        i = 0
    data_receive = s.recv(2048).decode() # Receive
    data_receive = data_receive.split(':/')
    if data_receive[0]=='ID002':
        print(data_receive[1])
    i +=1  
    time.sleep(1)
    