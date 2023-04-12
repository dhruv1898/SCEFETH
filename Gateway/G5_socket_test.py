import socket
from threading import Thread, Lock
from queue import Queue
from time import sleep, time
import os
import errno

Gateway_ID = '10.10.10.5'
HOST = '10.10.10.2'
PORT = 6006
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!!DISCONNECT!!"
n = 0
addr = (Gateway_ID, 5008)
finished_data_g2H = False

try:
    os.remove('h2g.txt')
except OSError:
    pass

try:
    os.remove('g2h.txt')
except OSError:
    pass

global_lock = Lock()

# Function to send data over Wifi.
def send_data_G2H(socket_to_habitat, msg):
    message_1 = msg.encode(FORMAT)
    msg_length = len(message_1)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    socket_to_habitat.send(send_length)
    socket_to_habitat.sendall(message_1)    
    with open('g2h.txt', 'a') as g2h:
        g2h.write(f'{message_1}\n')

# Receive data from Habitat.
#def Receive_data_H2G(socket_from_habitat, lock):        
 #   
  #      return data

# Receiver handler.
def handler_H2G(socket_from_habitat, lock):        
    h_connected = True
    while h_connected:
        with lock:
                with open('h2g.txt', 'a') as g2h:
                    g2h.write(f'new socket\n')
        msg_length = socket_from_habitat.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            data = socket_from_habitat.recv(msg_length).decode(FORMAT)
            with lock:
                with open('h2g.txt', 'a') as h2g:
                    h2g.write(f'{data}\n')        
        #data = Receive_data_H2G(socket_from_habitat, lock)
        if data == DISCONNECT_MESSAGE:
            h_connected = False
    socket_from_habitat.shutdown(socket.SHUT_RDWR)
    socket_from_habitat.close()

# Receiver loop for H2G.
def Receiver_H2G(addr, lock):
    G_server = socket.create_server(addr, family = socket.AF_INET, backlog = 5, reuse_port = True, dualstack_ipv6 = False)
    #G_server.bind(addr)
    G_server.listen(5)
    while True:
        socket_from_Habitat, addr = G_server.accept()
        handler_thread = Thread(target= handler_H2G, args=(socket_from_Habitat, lock))
        handler_thread.start()

if __name__ == '__main__':

    # create LoRa packets queue
    lora_queue = Queue()

    Receiver_H2G_thread = Thread(target= Receiver_H2G, args=(addr, global_lock))
    Receiver_H2G_thread.start()

    sleep(10)
    
    while True:
        # put lora recv in loop here and add the packets to the queue.
        lora_queue.put(f"Time is: {time()} and Data to Habitat{n}")
        if (not lora_queue.empty()) and not finished_data_g2H:
            data_to_Habitat = lora_queue.get()
            Gateway_Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            Gateway_Client.connect((HOST, PORT))
            send_data_G2H(Gateway_Client, data_to_Habitat)
            send_data_G2H(Gateway_Client, DISCONNECT_MESSAGE)
            try:
                Gateway_Client.recv(1024).decode(FORMAT)
            except socket.error as e:
                if e.errno != errno.ECONNRESET:
                    raise # Not error we are looking for
                pass # Handle error here.
                finished_data_g2H = True
        if finished_data_g2H:
            lora_queue.task_done()
            finished_data_g2H = False
        n += 1        