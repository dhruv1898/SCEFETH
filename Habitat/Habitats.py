#! /usr/bin/python3

# Author: Eenesh Chavan

### INFORMATION SPACE ###

# This is the Habitat software for using the SCEFETH network.


### IMPORTING LIBRARIES SPACE ###

from time import time, sleep
from socket import AF_INET, SOCK_STREAM, create_server, SHUT_RDWR, socket
from os import path, remove, listdir
from threading import Thread, active_count, RLock
import RPi.GPIO as GPIO
from ast import literal_eval
from numpy import float16, array, delete, argsort
from select import select
from logging import basicConfig, INFO, info, error, debug, critical
from copy import deepcopy

class Habitat():

    def __init__(self, Habitat_Time_LED:int, G2H_connection_LED:int, Geo_Table_update_LED:int, LoRa_packet_LED:int, Debug:bool, Logging:bool) -> None:

        self.DEBUG_ = Debug
        self.Gateway_ID = None
        self.Habitat_ID = "10.10.10.2"
        self.G2H_Port = 6006
        self.H2G_Port = 5008
        self.HEADER = 64
        self.FORMAT = "utf-8"
        self.DISCONNECT_MESSAGE = "!!DISCONNECT!!"
        self.file_path = path.abspath(path.dirname(__file__)) # file path of the running script.
        self.Habitat_Time_LED = Habitat_Time_LED # small red LED
        self.G2H_connection_LED = G2H_connection_LED # white LED
        self.Geo_Table_update_LED = Geo_Table_update_LED # red LED
        self.LoRa_packet_LED = LoRa_packet_LED # yellow LED
        self.file_ID = None
        self.Geo_table_update_dict = {'Gateway':[],'Enddevice':[],'Rssi':[]}
        self.test_result_e2h = None
        self.test_result_h2e = None
        # the Enddevices list at the Habitat.
        self.Enddevices = []
        # self.gatewaydata_dict_to_Enddevices: dictionary to list Gateways and the data to send to them to forward to Enddevices.
        # eg.: {'10.10.10.3':'{data}', '{data}'}
        self.gatewaydata_dict_to_Enddevices = {}
        self.LOG = Logging        


        #=== Task control variables: ===#                   

        # LOCKS
        self.h_sockets_inputs_list_lock = RLock()
        self.h_sockets_outputs_list_lock = RLock()
        self.h_sockets_exceptions_list_lock = RLock()
        self.gatewaydata_dict_to_Enddevices_lock = RLock()

        # LISTS
        # sockets list to read from @ Habitat.
        self.h_sockets_inputs = []
        # sockets list to write to @ Habitat.
        self.h_sockets_outputs = []
        # list to maintain exceptions from the sockets.
        self.h_sockets_exceptions = []

        if self.LOG:
            if path.exists(f"{self.file_path}/Habitat_log.log"):
                remove(f"{self.file_path}/Habitat_log.log")
            pass

        if self.LOG:
            # logging to file for debugging.
            basicConfig(filename=f"{self.file_path}/Habitat_log.log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=INFO)
        
        # GPIOS
        # use BOARD numbering for LEDs.
        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(self.Habitat_Time_LED, GPIO.OUT) 
        GPIO.setup(self.G2H_connection_LED, GPIO.OUT)
        GPIO.setup(self.Geo_Table_update_LED, GPIO.OUT)
        GPIO.setup(self.LoRa_packet_LED, GPIO.OUT)
        # keep all LEDs OFF at startup.
        GPIO.output(self.Habitat_Time_LED, GPIO.LOW)
        GPIO.output(self.G2H_connection_LED, GPIO.LOW)
        GPIO.output(self.Geo_Table_update_LED, GPIO.LOW)
        GPIO.output(self.LoRa_packet_LED, GPIO.LOW)

        # indicate script startup.
        if self.LOG:            
            info("Started Habitat script.")
        GPIO.output(self.Habitat_Time_LED, GPIO.HIGH)
        GPIO.output(self.G2H_connection_LED, GPIO.HIGH)
        GPIO.output(self.Geo_Table_update_LED, GPIO.HIGH)
        GPIO.output(self.LoRa_packet_LED, GPIO.HIGH)
        sleep(2)
        GPIO.output(self.Habitat_Time_LED, GPIO.LOW)
        GPIO.output(self.G2H_connection_LED, GPIO.LOW)
        GPIO.output(self.Geo_Table_update_LED, GPIO.LOW)
        GPIO.output(self.LoRa_packet_LED, GPIO.LOW)
        if self.LOG:           
            info("Waiting for OLSR to setup.")
        sleep(60) # wait for olsr to setup.
        # indicate olsr ready.
        if self.LOG:            
            info("Finished waiting for OLSR to setup.")
        GPIO.output(self.Habitat_Time_LED, GPIO.HIGH)
        GPIO.output(self.G2H_connection_LED, GPIO.HIGH)
        GPIO.output(self.Geo_Table_update_LED, GPIO.HIGH)
        GPIO.output(self.LoRa_packet_LED, GPIO.HIGH)
        sleep(2)
        GPIO.output(self.Habitat_Time_LED, GPIO.LOW)
        GPIO.output(self.G2H_connection_LED, GPIO.LOW)
        GPIO.output(self.Geo_Table_update_LED, GPIO.LOW)
        GPIO.output(self.LoRa_packet_LED, GPIO.LOW)


    #=== LED operation ===#  
  
    def Led_High(self, led) -> None:
    # Function to turn LED to HIGH.
        if self.LOG:
            debug(f"Setting the led: {led} HIGH.")
        GPIO.output(led, GPIO.HIGH)
    
    def Led_Low(self, led) -> None:
    # Function to turn LED to LOW.
        if self.LOG:
            debug(f"Setting the led: {led} LOW.")
        GPIO.output(led, GPIO.LOW)

    def Led_Blink(self, led, duration) -> None:
    # Function to blink the LED.
        if self.LOG:
            debug(f"Blinking the led: {led}.")
        self.Led_High(led)
        sleep(duration)
        self.Led_Low(led)


    #=== Create files for storing network test data. ===#
   
    def Remove_file(self, path) -> bool:
    # Remove if files already exist and create new.
        if path.exists(path):
            try:
                remove(path)
                open(path, "w")
            except:
                if self.LOG:
                    error(f"The file already exists and, Error in removing it and creating new.: {path}")
                if self.DEBUG_:
                    print(f"The file already exists and, Error in removing it and creating new.: {path}")
                return False
            else:
                if self.LOG:
                    debug(f"File already existed but, Deleted old and then Created new file: {path}")                
                if self.DEBUG_:
                    print(f"File already existed but, Deleted old and then Created new file: {path}")
                return True
        else:
            try:
                open(path, "w")
            except:
                if self.LOG:
                    error(f"Error in creating the file. {path}")
                if self.DEBUG_:
                    print(f"Error in creating the file. {path}")
                return False
            else:
                if self.LOG:
                    debug(f"Created file: {path}")
                if self.DEBUG_:
                    print(f"Created file: {path}")
                return True
    
    def Test_files(self) -> tuple:
    # Returns the path for E2H and H2E network test data files.
        last_file_ID = 0
        for fn in listdir(f"{self.file_path}/"):
            try:
                last_file_ID = max(last_file_ID, int(fn.split('#')[1]))
            except:                
                pass             
            
        if self.LOG:
            debug(f'The old file ID for storing test data was: {last_file_ID}')
        if self.DEBUG_:
            print(f'The old file ID for storing test data was: {last_file_ID}')
        self.file_ID = str(last_file_ID + 1)            
        self.test_result_e2h = f"{self.file_path}/Multihop_data_(@H)_E2H_#{self.file_ID}#.csv" 
        self.test_result_h2e = f"{self.file_path}/Multihop_data_(@H)_H2E_#{self.file_ID}#.csv"
        if self.Remove_file(self.test_result_e2h) and self.Remove_file(self.test_result_h2e):
            if self.LOG:                
                info(f'Created the files successfully: {self.test_result_e2h} and {self.test_result_h2e}')
            if self.DEBUG_:
                print(f'Created the files successfully: {self.test_result_e2h} and {self.test_result_h2e}')
            return self.test_result_e2h, self.test_result_h2e
        else:
            if self.LOG:
                critical("ERROR in creating the test files.")
            if self.DEBUG_:
                print("ERROR in creating the test files.")
            GPIO.output(self.Habitat_Time_LED, GPIO.HIGH)
            GPIO.output(self.G2H_connection_LED, GPIO.HIGH)
            GPIO.output(self.Geo_Table_update_LED, GPIO.HIGH)
            GPIO.output(self.LoRa_packet_LED, GPIO.HIGH)
            quit(1)

    def save_data_to_file(self, file_path, data_to_write) -> bool:
    # Function to write data to a file.
        try:
            with open(file_path, 'a') as file:
                file.write(data_to_write)
                file.write("\n")            
        except Exception as e:
            if self.LOG:
                error(f"Error in writing to file: {e}")
            if self.DEBUG_:
                print(f"Error in writing to file: {e}")
            return False
        else:
            if self.LOG:
                debug(f"Successfully written the data: {data_to_write} to the file_path: {file_path}")
            if self.DEBUG_:
                print(f"Successfully written the data: {data_to_write} to the file_path: {file_path}")
            return True


    #=== Select event loop functions ===#

    def h_sock_outputs_func(self, func_writeable) -> None:
    # Function to handle the output sockets.
        for h_sock in func_writeable:                               
            if self.LOG:                
                info(f"Writing on H2G pckt sending socket to the Gateway: {h_sock.getpeername()[0]}.") 
            if self.DEBUG_:
                print(f"Writing on H2G pckt sending socket to the Gateway: {h_sock.getpeername()[0]}.")

            # Loop to send all the data in the self.gatewaydata_dict_to_Enddevices dictionary to the gateway: h_sock.getpeername()[0].
            p_h = 0
            for i in range(0, len(self.gatewaydata_dict_to_Enddevices[h_sock.getpeername()[0]])):
                self.Led_High(self.G2H_connection_LED)
                self.Led_High(self.Habitat_Time_LED)
                if not self.send_data_H2G(h_sock, str(self.gatewaydata_dict_to_Enddevices[h_sock.getpeername()[0]][p_h])):
                    p_h+=1
                else:
                    if self.LOG:
                        debug(f"Sent this data: {self.gatewaydata_dict_to_Enddevices[h_sock.getpeername()[0]][p_h]} to Gateway: {h_sock.getpeername()[0]}")                       
                    if self.DEBUG_:
                        print(f"Sent this data: {self.gatewaydata_dict_to_Enddevices[h_sock.getpeername()[0]][p_h]} to Gateway: {h_sock.getpeername()[0]}")                            
                    save = deepcopy(self.gatewaydata_dict_to_Enddevices[h_sock.getpeername()[0]][p_h])                            
                    save['Time'], save['Gateway'] = str(time()), h_sock.getpeername()[0]                            
                    self.save_data_to_file(self.test_result_h2e, str(save))
                    self.gatewaydata_dict_to_Enddevices[h_sock.getpeername()[0]].pop(p_h)
                                    
            self.send_data_H2G(h_sock, self.DISCONNECT_MESSAGE)          
            try:
                h_sock.shutdown(SHUT_RDWR)
                h_sock.close()                        
            except Exception as e:
                if self.LOG:
                    error(f"Error in closing the H2G socket @H: {e}")
                if self.DEBUG_:
                    print(f"Error in closing the H2G socket @H: {e}")
                with self.h_sockets_outputs_list_lock:
                    self.h_sockets_outputs.remove(h_sock)
                self.Led_Low(self.G2H_connection_LED)
                self.Led_Low(self.Habitat_Time_LED)              
            else:
                with self.h_sockets_outputs_list_lock and self.h_sockets_exceptions_list_lock:
                    self.h_sockets_outputs.remove(h_sock)
                    self.h_sockets_exceptions.remove(h_sock)
                if self.LOG:                    
                    info("!!!CLOSED!!! H2G socket @H.")
                if self.DEBUG_:
                    print("!!!CLOSED!!! the H2G socket @H.")
                self.Led_Low(self.G2H_connection_LED)
                self.Led_Low(self.Habitat_Time_LED)                 

    def h_sock_inputs_func(self, func_readable, func_H_server) -> None:
    # Function to handle the input sockets.
        for h_sock in func_readable:

            if h_sock is func_H_server:
                if self.LOG:                    
                    info("Receiving on G2H socket to accept connection from a Gateway.")
                if self.DEBUG_:
                    print("Receiving on G2H socket to accept connection from a Gateway.")

                socket_from_Gateway, addr_g = func_H_server.accept()
                if self.LOG:                    
                    info(f"Receiving on G2H socket, Accepted connection from {addr_g}.")
                with self.h_sockets_inputs_list_lock and self.h_sockets_exceptions_list_lock:
                    self.h_sockets_inputs.append(socket_from_Gateway)
                    self.h_sockets_exceptions.append(socket_from_Gateway) 

            else:                
                h_sock.settimeout(1)
                if self.LOG:                    
                    info("Receiving on G2H socket to receive data from Gateway.")
                if self.DEBUG_:
                    print("Receiving on G2H socket to receive data from Gateway.")
                try:
                    msg_length = h_sock.recv(self.HEADER).decode(self.FORMAT)
                except Exception as e:
                    if self.LOG:
                        error(f"Error in h_sock readable @ msg_length = h_sock.recv : {e}")
                    try:
                        h_sock.shutdown(SHUT_RDWR)
                        h_sock.close()                                                
                    except Exception as e:
                        if self.LOG:
                            error(f"Error in closing the G2H socket @ H: {e}")
                        if self.DEBUG_:
                            print(f"Error in closing the G2H socket @ H: {e}")
                        with self.h_sockets_inputs_list_lock:
                            self.h_sockets_inputs.remove(h_sock)                        
                    else:
                        with self.h_sockets_inputs_list_lock and self.h_sockets_exceptions_list_lock:
                            self.h_sockets_inputs.remove(h_sock)
                            self.h_sockets_exceptions.remove(h_sock)
                        if self.LOG:                            
                            info("!!!CLOSED!!! the G2H socket @ H.")
                        if self.DEBUG_:
                            print("!!!CLOSED!!! the G2H socket @ H.")
                else:
                    if msg_length:
                        try:
                            self.Led_High(self.G2H_connection_LED)
                            msg_length = int(msg_length)
                        except Exception as e:
                            if self.LOG:
                                error(f"Error in reading msg_length as integer: {e}")
                            if self.DEBUG_:
                                print(f"Error in reading msg_length as integer: {e}")                            
                            try:
                                h_sock.shutdown(SHUT_RDWR)
                                h_sock.close()                        
                            except Exception as e:
                                if self.LOG:
                                    error(f"Error in closing the G2H socket @ H: {e}")
                                if self.DEBUG_:
                                    print(f"Error in closing the G2H socket @ H: {e}")
                                with self.h_sockets_inputs_list_lock:
                                    self.h_sockets_inputs.remove(h_sock)
                                self.Led_Low(self.G2H_connection_LED)
                            else:
                                with self.h_sockets_inputs_list_lock and self.h_sockets_exceptions_list_lock:
                                    self.h_sockets_inputs.remove(h_sock)
                                    self.h_sockets_exceptions.remove(h_sock)
                                if self.LOG:                                    
                                    info("!!!CLOSED!!! the G2H socket @ H.")
                                if self.DEBUG_:
                                    print("!!!CLOSED!!! the G2H socket @ H.")  
                                self.Led_Low(self.G2H_connection_LED)
                        else:
                            try:
                                data = h_sock.recv(msg_length).decode(self.FORMAT)            
                                if self.LOG:
                                    debug(f"Received message from Gateway: {data}")
                                if self.DEBUG_:
                                    print(f"Received message from Gateway: {data}")                  
                                if data == self.DISCONNECT_MESSAGE:                    
                                    try:
                                        h_sock.shutdown(SHUT_RDWR)
                                        h_sock.close()                        
                                    except Exception as e:
                                        if self.LOG:
                                            error(f"Error in closing the G2H socket @ H: {e}")
                                        if self.DEBUG_:
                                            print(f"Error in closing the G2H socket @ H: {e}")
                                        with self.h_sockets_inputs_list_lock:
                                            self.h_sockets_inputs.remove(h_sock)
                                        self.Led_Low(self.G2H_connection_LED)                                        
                                    else:
                                        with self.h_sockets_inputs_list_lock and self.h_sockets_exceptions_list_lock:
                                            self.h_sockets_inputs.remove(h_sock)
                                            self.h_sockets_exceptions.remove(h_sock)
                                        if self.LOG:                                            
                                            info("!!!CLOSED!!! the G2H socket @ H.")
                                        if self.DEBUG_:
                                            print("!!!CLOSED!!! the G2H socket @ H.")  
                                    self.Led_Low(self.G2H_connection_LED)                                     
                                else:
                                    self.saving(self.test_result_e2h, data, h_sock.getpeername())  
                            except Exception as e:
                                if self.LOG:
                                    error(f"Error in h_sock readable @ data = h_sock.recv : {e}")
                                if self.DEBUG_:
                                    print(f"Error in h_sock readable @ data = h_sock.recv : {e}")
                                try:
                                    h_sock.shutdown(SHUT_RDWR)
                                    h_sock.close()                                                           
                                except Exception as e:
                                    if self.LOG:
                                        error(f"Error in closing the G2H socket @ H: {e}")
                                    if self.DEBUG_:
                                        print(f"Error in closing the G2H socket @ H: {e}")
                                    with self.h_sockets_inputs_list_lock:
                                        self.h_sockets_inputs.remove(h_sock)
                                    self.Led_Low(self.G2H_connection_LED)
                                else:
                                    with self.h_sockets_inputs_list_lock and self.h_sockets_exceptions_list_lock:
                                        self.h_sockets_inputs.remove(h_sock)
                                        self.h_sockets_exceptions.remove(h_sock)
                                    if self.LOG:                                       
                                        info("!!!CLOSED!!! the G2H socket @ H.")
                                    if self.DEBUG_:
                                        print("!!!CLOSED!!! the G2H socket @ H.")
                                    self.Led_Low(self.G2H_connection_LED)                  
        
    def h_sock_exceptions_func(self, func_exceptions) -> None:
    # Function to handle the exceptions in the sockets.
        for h_sock in func_exceptions:
            if self.LOG:
                error("Exception in socket @H.")     
            if self.DEBUG_:
                print("Exception in socket @H.")                               
            with self.h_sockets_inputs_list_lock and self.h_sockets_exceptions_list_lock:
                try:
                    self.h_sockets_exceptions.remove(h_sock)
                    self.h_sockets_inputs.remove(h_sock)                        
                except Exception as e:
                    if self.LOG:
                        error(f"Error in removing socket from self.h_sockets_inputs_list in h_exceptional: {e}")
                    pass
            with self.h_sockets_outputs_list_lock and self.h_sockets_exceptions_list_lock:
                try:
                    self.h_sockets_exceptions.remove(h_sock) 
                    self.h_sockets_outputs.remove(h_sock)                                               
                except Exception as e:
                    if self.LOG:
                        error(f"Error in removing socket from self.h_sockets_outputs_list in h_exceptional: {e}")
                    pass 
            try:
                h_sock.shutdown(SHUT_RDWR)
                h_sock.close()                        
            except Exception as e:
                if self.LOG:
                    error(f"Error in closing the socket @ H: {e}")
                if self.DEBUG_:
                    print(f"Error in closing the socket @ H: {e}")
                self.Led_Low(self.G2H_connection_LED)
            else:
                if self.LOG:                        
                    info("!!!CLOSED!!! the socket @ H.")
                if self.DEBUG_:
                    print("!!!CLOSED!!! the socket @ H.") 
                self.Led_Low(self.G2H_connection_LED)        

    def select_event_loop_handler_func(self) -> None:
    # Select Event Loop handler function. 
        H_server = create_server((self.Habitat_ID, self.G2H_Port), family = AF_INET, backlog = 5, reuse_port = True, dualstack_ipv6 = False)
        H_server.listen(5) 

        with self.h_sockets_inputs_list_lock and self.h_sockets_exceptions_list_lock:
            self.h_sockets_inputs.append(H_server)
            self.h_sockets_exceptions.append(H_server)   
        
        while True:
            if self.LOG:
                debug("Waiting in the select event loop handler.")   
            if self.DEBUG_:
                print("Waiting in the select event loop handler.")         
            with self.h_sockets_inputs_list_lock and self.h_sockets_outputs_list_lock and self.h_sockets_exceptions_list_lock:
                h_readable,h_writeable,h_exceptional = select(self.h_sockets_inputs,self.h_sockets_outputs,self.h_sockets_inputs,0.5)            
            if self.LOG:
                debug("Got something from the select in the select_event_loop_handler.")
            if self.DEBUG_:
                print("Got something from the select in the select_event_loop_handler.")

            h_sock_outputs_thread = Thread(target=self.h_sock_outputs_func, args=(h_writeable,))
            h_sock_outputs_thread.start()                    
        
            h_sock_inputs_thread = Thread(target=self.h_sock_inputs_func, args=(h_readable, H_server))
            h_sock_inputs_thread.start()            
        
            h_sock_exceptions_thread = Thread(target=self.h_sock_exceptions_func, args=(h_exceptional,))
            h_sock_exceptions_thread.start()   

            h_sock_outputs_thread.join()
            h_sock_inputs_thread.join()
            h_sock_exceptions_thread.join()               

            self.get_thread_number()           
                    
    def select_event_loop_thread(self) -> None:
    # Function to start the select event loop thread.
        event_loop_thread = Thread(target=self.select_event_loop_handler_func, args=())
        event_loop_thread.daemon = True
        event_loop_thread.start()


    #=== E2H functions ===#

    def saving(self, to_file, data_in, addr_g) -> None:
    # Function to parse and save the data received from the input sockets.
        try:
            if self.LOG:
                debug(f"Trying to read the received data_in as a dictionary: {data_in}")
            # read the received data_in as a dictionary.
            data = literal_eval(data_in)
        except Exception as e:
            if self.LOG:
                error(f"Error in reading the G2H data_in:{data_in} as dictionary: {e}")
            if self.DEBUG_:
                print(f"Error in reading the G2H data_in:{data_in} as dictionary: {e}")
            pass
        else:          
            try:
                # check if E2H packet received.
                if 'Gateway' not in data:
                    try:  
                        self.Led_High(self.LoRa_packet_LED)  
                        save_D_dict = str({'Time':str(time()),'Gateway':addr_g[0],'Port':str(addr_g[1]),'ID':data['ID'],'Message':data['Message'],'Packetno.':data['Packetno.'],'Mode':'E2H'})
                    except Exception as e:
                        if self.DEBUG_:
                            print(f"Error in formatting the save_D_dict in saving: {e}") 
                        self.Led_Low(self.LoRa_packet_LED)
                    else:       
                        with open(to_file, 'a') as e2h_file:
                            e2h_file.write(save_D_dict)
                            e2h_file.write("\n")
                        if self.LOG:
                            debug(f"Written the pckt: {save_D_dict} receved, to file: {to_file}.")
                        if self.DEBUG_:
                            print(f"Written the pckt: {save_D_dict} receved, to file: {to_file}.")
                        self.Led_Low(self.LoRa_packet_LED)   
                else:
                    # check if Geo Table received. 
                    try:
                        if self.LOG:                        
                            debug("Trying to parse over the received table.")
                        if self.DEBUG_:                            
                            print("Trying to parse over the received table.")
                        self.Led_High(self.Geo_Table_update_LED)
                        Geo_table_update_recv_dict = data
                        Gateway_array = array(self.Geo_table_update_dict['Gateway'])
                        Enddevice_array = array(self.Geo_table_update_dict['Enddevice'])
                        Rssi_array = array(self.Geo_table_update_dict['Rssi'])
                        idx_list = [i for i, e in enumerate(self.Geo_table_update_dict['Gateway']) if e == Geo_table_update_recv_dict['Gateway']]
                        # print(Geo_table_update_dict)
                        Gateway_array = delete(Gateway_array, idx_list)
                        Enddevice_array = delete(Enddevice_array, idx_list)
                        Rssi_array = delete(Rssi_array, idx_list)
                        self.Geo_table_update_dict['Gateway']=list(Gateway_array)
                        self.Geo_table_update_dict['Enddevice']=list(Enddevice_array)
                        self.Geo_table_update_dict['Rssi']=list(Rssi_array)
                        for i in range(len(Geo_table_update_recv_dict['Enddevice'])):
                            self.Geo_table_update_dict['Gateway'].append(data['Gateway'])
                            self.Geo_table_update_dict['Enddevice'].append(Geo_table_update_recv_dict['Enddevice'][i])
                            self.Geo_table_update_dict['Rssi'].append(Geo_table_update_recv_dict['Rssi'][i])                    
                    except Exception as e:
                        if self.LOG:
                            error(f"Error in parsing over the received table: {e}")
                        if self.DEBUG_:
                            print(f"Error in parsing over the received table: {e}") 
                        pass
                    else:
                        if self.LOG:
                            debug(f"Successfully parsed and received the table, current table @ H: {self.Geo_table_update_dict}")                        
                        if self.DEBUG_:
                            print(f"Successfully parsed and received the table, current table @ H: {self.Geo_table_update_dict}")
                        self.Led_Low(self.Geo_Table_update_LED)
            except Exception as e:
                if self.LOG:
                    error(f"Error in parsing over the data received from the Gateway: {e}")
                if self.DEBUG_:
                    print(f"Error in parsing over the data received from the Gateway: {e}")
                pass

    
    #=== End-devices functions ===#

    def update_Enddevices_at_Habitat(self, id_list:list) -> None:
    # Function to update the Enddevices list at the Habitat.
        self.Enddevices = id_list


    #=== H2E functions ===#

    def send_data_H2G(self, socket_to_gateway, msg) -> bool:
    # Function to send the data through the output sockets.
        try:
            if self.LOG:
                debug(f"Trying to send the msg to Gateway: {msg}")
            encoded_msg = msg.encode(self.FORMAT)
            msg_length = len(encoded_msg)
            send_length = str(msg_length).encode(self.FORMAT)
            send_length += b' ' * (self.HEADER - len(send_length))
            socket_to_gateway.sendall(send_length)
            socket_to_gateway.sendall(encoded_msg)
        except Exception as e:
            if self.LOG:
                error(f"Got this error in sending data to Gateway: {e}")
            if self.DEBUG_:
                print(f"Got this error in sending data to Gateway: {e}")
            return False
        else:
            if self.LOG:
                debug(f"Successfully sent the msg to Gateway: {msg}")
            if self.DEBUG_:
                print(f"Successfully sent the msg to Gateway: {msg}")
            return True

    def G_list_for_H2E(self, Enddeviceid) -> tuple:
    # Function to return the Enddevice id (str) and list of Gateways to reach the End-device.
        Gateway_array = array(self.Geo_table_update_dict['Gateway'])        
        Rssi_array = array(self.Geo_table_update_dict['Rssi'], dtype=float16)
        idx_list = [i for i, e in enumerate(self.Geo_table_update_dict['Enddevice']) if e == Enddeviceid]
        if len(idx_list)>0:            
            Gateway_array = Gateway_array[idx_list]            
            Rssi_array = Rssi_array[idx_list]
            sort_list = argsort(-Rssi_array)
            Gateway_array = Gateway_array[sort_list]           
            Rssi_array = Rssi_array[sort_list]            
            return Enddeviceid, Gateway_array             
        else:            
            if self.LOG:
                debug("ID not found in the network! Please try a different ID :D")
            if self.DEBUG_:
                print("ID not found not found in the network! Please try a different ID :D")
            return Enddeviceid, None

    def create_conn_to_G_for_H2E(self, Node: str, Gateway_list: list, data2e) -> bool: 
    # Function to create a connection to Gateway for H2G communication.        
        if self.LOG:
            debug("Creating socket for sending pckts to End-device.")
        Habitat_client = socket(AF_INET,SOCK_STREAM)
        Habitat_client.settimeout(1)
        for addr in Gateway_list:            
            if self.LOG:                
                info(f"Connecting to Gateway: {addr} to forward the pckt to End-device: {Node}.")
            h2g_ret = Habitat_client.connect_ex((addr,self.H2G_Port))                    
            if h2g_ret == 0:
                if self.LOG:                      
                    info(f"Connected to Gateway: {addr} to forward the pckt to End-device: {Node}.")  
                data2e['Gateway'] = Habitat_client.getpeername()[0]                          
                try:
                    with self.gatewaydata_dict_to_Enddevices_lock:
                        self.gatewaydata_dict_to_Enddevices[Habitat_client.getpeername()[0]].append(data2e)                    
                except Exception as e:
                    if self.LOG:
                        error(f'Gateway {Habitat_client.getpeername()[0]} not found in self.gatewaydata_dict_to_Enddevices, creating key and appending data: {e}')
                    with self.gatewaydata_dict_to_Enddevices_lock:
                        self.gatewaydata_dict_to_Enddevices[Habitat_client.getpeername()[0]]=[]
                        self.gatewaydata_dict_to_Enddevices[Habitat_client.getpeername()[0]].append(data2e)
                    with self.h_sockets_outputs_list_lock:
                        self.h_sockets_outputs.append(Habitat_client)
                    with self.h_sockets_exceptions_list_lock:
                        self.h_sockets_exceptions.append(Habitat_client)
                    return False
                else:
                    with self.h_sockets_outputs_list_lock:
                        self.h_sockets_outputs.append(Habitat_client)
                    with self.h_sockets_exceptions_list_lock:
                        self.h_sockets_exceptions.append(Habitat_client)
                    return True
            else:
                if self.LOG:
                    error(f'Failed to connect to Gateway {addr}, to forward the pckt to End-device: {Node}.')
                pass
        if self.LOG:
            error(f"Failed to create socket for sending data:{data2e} to End-device:{Node}.")
        return False
    
    def get_thread_number(self) -> None:
    # Function to get the number of threads running, and quit if less than 2.        
        if active_count() < 2:
            if self.LOG:
                critical(f"Current running thread numbers = {active_count()}, hence quiting.")
            if self.DEBUG_:
                print(f"Current running thread numbers = {active_count()}, hence quiting.")
            GPIO.output(self.Habitat_Time_LED, GPIO.HIGH)
            GPIO.output(self.G2H_connection_LED, GPIO.HIGH)
            GPIO.output(self.Geo_Table_update_LED, GPIO.HIGH)
            GPIO.output(self.LoRa_packet_LED, GPIO.HIGH)
            quit(1)