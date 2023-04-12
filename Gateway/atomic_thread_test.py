from threading import Thread
from time import sleep

send_data_finished = True

def test_func():
    global send_data_finished
    print("Started function now!")
    sleep(2)
    print("finished function now!")
    send_data_finished = True

while True:
    if send_data_finished:
        send_data_finished = False
        to_run = Thread(target=test_func)
        to_run.start()
    
