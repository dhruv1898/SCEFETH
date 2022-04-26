import socket
HOST='10.10.10.4' #change IP address for each Gateway here
PORT=50001
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((HOST,PORT))
s.listen(10)
while True:
        conn,addr=s.accept()
        data=conn.recv(4096).decode()
        print(data)
        conn.close()
s.close()
