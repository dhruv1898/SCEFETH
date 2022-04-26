import numpy as np
from time import sleep
import socket
import csv
while True:
        HOST = '10.10.10.2'
        PORT = 50007
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST,PORT))
        data_string = "10.10.10.4:"
        with open('Enddevice.csv') as file_obj:
                reader_obj = csv.reader(file_obj)
                for row in reader_obj:
                        data_string = data_string+str(row)+";"
        s.send(data_string.encode())
        print(data_string)
        s.close()
        sleep(10)
