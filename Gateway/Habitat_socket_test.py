import socket
from threading import Thread, Lock
from queue import Queue
from time import sleep, time
import os
import errno

Gateway_ID_5 = '10.10.10.5'
Gateway_ID_3 = '10.10.10.3'
HOST = '10.10.10.2'
PORT = 5008
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!!DISCONNECT!!"
n = 0
addr = (HOST, 6006)
finished_data_H2g = False

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
def send_data_H2G(socket_to_gateway, msg):
    message_1 = msg.encode(FORMAT)
    msg_length = len(message_1)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    socket_to_gateway.send(send_length)
    socket_to_gateway.sendall(message_1)
    with open('h2g.txt', 'a') as h2g:
        h2g.write(f'{message_1}\n')

# Receive data from Gateway.
#def Receive_data_G2H(socket_from_gateway, lock):        
#
    #return data       

# Receiver handler.
def handler_G2H(socket_from_gateway, lock):        
    g_connected = True
    while g_connected: 
        with lock:
                with open('g2h.txt', 'a') as g2h:
                    g2h.write(f'new socket\n')
        msg_length = socket_from_gateway.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            data = socket_from_gateway.recv(msg_length).decode(FORMAT)
            with lock:
                with open('g2h.txt', 'a') as g2h:
                    g2h.write(f'{data}\n')        
        if data == DISCONNECT_MESSAGE:
            g_connected = False
    socket_from_gateway.shutdown(socket.SHUT_RDWR)
    socket_from_gateway.close()

# Receiver loop for H2G.
def Receiver_G2H(addr, lock):
    H_server = socket.create_server(addr, family = socket.AF_INET, backlog = 5, reuse_port = True, dualstack_ipv6 = False)
    #G_server.bind(addr)
    H_server.listen(5)
    while True:
        socket_from_Gateway, addr = H_server.accept()
        handler_thread = Thread(target= handler_G2H, args=(socket_from_Gateway, lock))
        handler_thread.start()

if __name__ == '__main__':

    # create Habitat packets queue
    h2e_queue = Queue()

    Receiver_G2H_thread = Thread(target= Receiver_G2H, args=(addr, global_lock))
    Receiver_G2H_thread.start()
    
    sleep(10)

    while True:
        # put data production here and add packets to the queue.
        if n % 2 == 0:
            h2e_queue.put((Gateway_ID_5, f"Time is: {time()} and Data to End-device {n}"))
        else:
            h2e_queue.put((Gateway_ID_3, f"Time is: {time()} and Data to End-device {n}"))
        if (not h2e_queue.empty()) and not finished_data_H2g:
            get_queue_data = h2e_queue.get()
            Habitat_Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            Habitat_Client.connect((get_queue_data[0], PORT))
            send_data_H2G(Habitat_Client, get_queue_data[1])
            send_data_H2G(Habitat_Client, DISCONNECT_MESSAGE)
            try:
                Habitat_Client.recv(1024).decode(FORMAT)
            except socket.error as e:
                if e.errno != errno.ECONNRESET:
                    raise # Not error we are looking for
                pass # Handle error here.
                finished_data_H2g = True
        if finished_data_H2g:
            h2e_queue.task_done()
            finished_data_H2g = False
        n += 1        