#! /usr/bin/python3

# Author: Eenesh Chavan

### INFORMATION SPACE ###

# This is the Gateway software for using the SCEFETH network.

# Note:
# 1) rf95.py should be kept in the same folder as this script.
# 2) The rf95 library keeps the transceiver in RX mode with the available function.
# 3) The send function puts the transceiver in TX mode before sending.
# 4) Max length for sending a LoRa packet is 255 bytes.


### IMPORTING LIBRARIES SPACE ###

from rf95 import RF95, Bw125Cr45Sf128
from time import time, sleep
from socket import AF_INET, SOCK_STREAM, create_server, SHUT_RDWR, socket
from os import path, remove, listdir
from ntplib import NTPClient
from threading import Thread, RLock, active_count
import RPi.GPIO as GPIO
from ast import literal_eval
from logging import basicConfig, INFO, info, error, debug, critical
from select import select

class Gateway():

    def __init__(self, Gateway_number:int, Dragino_spi_channel:int, Dragino_cs_pin:int, Dragino_reset_pin:int, \
                Gateway_Time_LED:int, G2H_connection_LED:int, Geo_Table_update_LED:int, LoRa_packet_LED:int, \
                Debug:bool, Logging: bool) -> None:

        self.DEBUG_ = Debug
        self.Gateway_ID = f"10.10.10.{Gateway_number}"
        self.Habitat_ID = "10.10.10.2"
        self.G2H_Port = 6006
        self.H2G_Port = 5008
        self.HEADER = 64
        self.FORMAT = "utf-8"
        self.DISCONNECT_MESSAGE = "!!DISCONNECT!!"
        self.time_correction = 0
        self.file_path = path.abspath(path.dirname(__file__)) # file path of the running script.
        self.Gateway_Time_LED = Gateway_Time_LED # small red LED
        self.G2H_connection_LED = G2H_connection_LED # white LED
        self.Geo_Table_update_LED = Geo_Table_update_LED # red LED
        self.LoRa_packet_LED = LoRa_packet_LED # yellow LED
        self.file_ID = None
        self.Geo_table_dict = {'Gateway': self.Gateway_ID, 'Enddevice':[],'Rssi':[], 'Time':[]}
        self.G_when_time_synced = None
        self.geo_table_delta_time = time()
        self.geo_table_success_delta_time = time()
        self.check_ID_delta_time = time()
        self.LOG = Logging

       
        #=== Task control variables: ===#

        # LOCKS
        self.g_sockets_inputs_list_lock = RLock()
        self.g_sockets_outputs_list_lock = RLock()
        self.g_sockets_exceptions_list_lock = RLock()
        self.geo_table_list_lock = RLock()
        self.from_lora_lock = RLock()
        self.to_lora_lock = RLock()
        self.time_correction_lock = RLock()
        self.e2h_file_lock = RLock()
        self.h2e_file_lock = RLock()
        self.Geo_table_dict_lock = RLock()        

        # STATES
        self.initialized = False
        self.G_time_synced = False

        # LISTS
        # list to hold packets to send over lora.
        self.to_lora = []
        # list to hold packets received over lora.
        self.from_lora = []        
        # list to hold the Geo table.
        self.geo_table_list = []
        # sockets list to read from @ Gateway.
        self.g_sockets_inputs = []
        # sockets list to write to @ Gateway.
        self.g_sockets_outputs = []   
        # list to maintain exceptions from the sockets.
        self.g_sockets_exceptions = []     

        if self.LOG:
            if path.exists(f"{self.file_path}/Gateway_log.log"):
                remove(f"{self.file_path}/Gateway_log.log")
            pass

        if self.LOG:
            # logging to file for debugging.
            basicConfig(filename=f"{self.file_path}/Gateway_log.log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=INFO)
        
        # GPIOS
        # use BOARD numbering for LEDs and rf95.
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        GPIO.setup(self.Gateway_Time_LED, GPIO.OUT) 
        GPIO.setup(self.G2H_connection_LED, GPIO.OUT)
        GPIO.setup(self.Geo_Table_update_LED, GPIO.OUT)
        GPIO.setup(self.LoRa_packet_LED, GPIO.OUT)
        # keep all LEDs OFF at startup.
        GPIO.output(self.Gateway_Time_LED, GPIO.LOW)
        GPIO.output(self.G2H_connection_LED, GPIO.LOW)
        GPIO.output(self.Geo_Table_update_LED, GPIO.LOW)
        GPIO.output(self.LoRa_packet_LED, GPIO.LOW)

        # indicate script startup
        if self.LOG:
            info("Started Gateway script.")
        GPIO.output(self.Gateway_Time_LED, GPIO.HIGH)
        GPIO.output(self.G2H_connection_LED, GPIO.HIGH)
        GPIO.output(self.Geo_Table_update_LED, GPIO.HIGH)
        GPIO.output(self.LoRa_packet_LED, GPIO.HIGH)
        sleep(2)
        GPIO.output(self.Gateway_Time_LED, GPIO.LOW)
        GPIO.output(self.G2H_connection_LED, GPIO.LOW)
        GPIO.output(self.Geo_Table_update_LED, GPIO.LOW)
        GPIO.output(self.LoRa_packet_LED, GPIO.LOW)
        if self.LOG:
            info("Waiting for OLSR to setup.")
        sleep(60) # wait for olsr to setup.
        # indicate olsr ready.
        if self.LOG:
            info("Finished waiting for OLSR to setup.")
        GPIO.output(self.Gateway_Time_LED, GPIO.HIGH)
        GPIO.output(self.G2H_connection_LED, GPIO.HIGH)
        GPIO.output(self.Geo_Table_update_LED, GPIO.HIGH)
        GPIO.output(self.LoRa_packet_LED, GPIO.HIGH)
        sleep(2)
        GPIO.output(self.Gateway_Time_LED, GPIO.LOW)
        GPIO.output(self.G2H_connection_LED, GPIO.LOW)
        GPIO.output(self.Geo_Table_update_LED, GPIO.LOW)
        GPIO.output(self.LoRa_packet_LED, GPIO.LOW)


        #=== LoRa Initialization ===#

        self.Dragino_Lora = RF95(Dragino_spi_channel, Dragino_cs_pin, Dragino_reset_pin)
        if not self.Dragino_Lora.init(): # returns True if found
            if self.LOG:
                critical("Dragino module not found.")
            if self.DEBUG_:
                print("Dragino module not found")
            GPIO.output(self.Gateway_Time_LED, GPIO.HIGH)
            GPIO.output(self.G2H_connection_LED, GPIO.HIGH)
            GPIO.output(self.Geo_Table_update_LED, GPIO.HIGH)
            GPIO.output(self.LoRa_packet_LED, GPIO.HIGH)
            quit(1)
        else:
            if self.LOG:
                info("Dragino module found.")
            if self.DEBUG_:
                print("Dragino module found.")
            pass

        # set frequency, power and mode
        self.Dragino_Lora.set_frequency(868.0) # in MHz.
        self.Dragino_Lora.set_tx_power(14) # in dBm.
        self.Dragino_Lora.set_preamble_length(8)
        # LoRa parameters info:
        #!!! using implicit mode because Lopy doesn't support explicit mode. !!!#
        # Bw125Cr45Sf128 : Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on. Default medium range.
        # Bw500Cr45Sf128 : Bw = 500 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on. Fast+short range.
        # Bw31_25Cr48Sf512 : Bw = 31.25 kHz, Cr = 4/8, Sf = 512chips/symbol, CRC on. Slow+long range.
        # Bw125Cr48Sf4096 : Bw = 125 kHz, Cr = 4/8, Sf = 4096chips/symbol, CRC on. Slow+long range.
        self.Dragino_Lora.set_modem_config(Bw125Cr45Sf128)        
        #self.Dragino_Lora.set_modem_config_custom(bandwidth = rf95.BW_125KHZ, coding_rate = rf95.CODING_RATE_4_7, implicit_header = rf95.IMPLICIT_HEADER_MODE_ON, spreading_factor = rf95.SPREADING_FACTOR_1024CPS, \
        #                                          crc = rf95.RX_PAYLOAD_CRC_ON, continuous_tx = rf95.TX_CONTINUOUS_MODE_OFF, timeout = rf95.SYM_TIMEOUT_MSB, agc_auto = rf95.AGC_AUTO_OFF)


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
   
    def Remove_file(self, path_) -> bool:
    # Remove if files already exist and create new.
        if path.exists(path_):
            try:
                remove(path_)
                open(path_, "w")
            except:
                if self.LOG:
                    error(f"The file already exists and, Error in removing it and creating new.: {path_}")
                if self.DEBUG_:
                    print(f"The file already exists and, Error in removing it and creating new.: {path_}")
                return False
            else:
                if self.LOG:
                    debug(f"File already existed but, Deleted old and then Created new file: {path_}")                
                if self.DEBUG_:
                    print(f"File already existed but, Deleted old and then Created new file: {path_}")
                return True
        else:
            try:
                open(path_, "w")
            except:
                if self.LOG:
                    error(f"Error in creating the file. {path_}")
                if self.DEBUG_:
                    print(f"Error in creating the file. {path_}")
                return False
            else:
                if self.LOG:
                    debug(f"Created file: {path_}")
                if self.DEBUG_:
                    print(f"Created file: {path_}")
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
        self.test_result_e2h = f"{self.file_path}/Multihop_data_(@G)_E2H_#{self.file_ID}#.csv" 
        self.test_result_h2e = f"{self.file_path}/Multihop_data_(@G)_H2E_#{self.file_ID}#.csv"
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
            GPIO.output(self.Gateway_Time_LED, GPIO.HIGH)
            GPIO.output(self.G2H_connection_LED, GPIO.HIGH)
            GPIO.output(self.Geo_Table_update_LED, GPIO.HIGH)
            GPIO.output(self.LoRa_packet_LED, GPIO.HIGH)
            quit(1)

    def save_data_to_file(self, file_path, data_to_write) -> bool:
    # Function to save data to a file.
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


    #=== Time synchronization ===#
    
    def Time_Sync(self) -> None:   
    # Function for syncing the clocks of the Gateways with that of Habitat's. 
        try:
            if self.LOG:
                debug("Trying time synchronization with Habitat.")
            if self.DEBUG_:
                print("Trying time synchronization with Habitat.")
            c = NTPClient()
            response = c.request(self.Habitat_ID)
            with self.time_correction_lock:
                self.time_correction = response.tx_time - time()  # response.tx_time is the time of the server.                                        
        except Exception as e:
            if self.LOG:
                error(f"Error in syncing time: {e}")
            if self.DEBUG_:
                print(f"Error in syncing time: {e}")
            self.G_time_synced = False
            self.G_when_time_synced = time()
        else:
            if self.LOG:
                info("Time synced with Habitat.")
                #debug(f"The correction for Gateway's clock is {self.time_correction} seconds.")
            if self.DEBUG_:
                print("Time synced with Habitat.")
                #print(f"The correction for Gateway's clock is {self.time_correction} seconds.")
            self.Led_High(self.Gateway_Time_LED) 
            self.G_time_synced = True   
            self.G_when_time_synced = time()


    #=== E2H functions ===#

    def store_ID(self, id_data) -> None:
    # Function to store End-device Id in the Gateway's Geo Table.
        with self.Geo_table_dict_lock:
            if id_data['ID'] in self.Geo_table_dict['Enddevice']:
                idx = self.Geo_table_dict['Enddevice'].index(id_data['ID'])
                del self.Geo_table_dict['Enddevice'][idx]
                del self.Geo_table_dict['Rssi'][idx]
                del self.Geo_table_dict['Time'][idx]
            self.Geo_table_dict['Enddevice'].append(id_data['ID'])
            self.Geo_table_dict['Rssi'].append(id_data['RSSI'])
            self.Geo_table_dict['Time'].append(time())
            if self.LOG:
                debug(f"Storing ID to the Geo table, current table: {self.Geo_table_dict}")
            if self.DEBUG_:
                print(f"Storing ID to the Geo table, current table: {self.Geo_table_dict}")

    def check_ID_time(self) -> None:
    # Function to remove the End-device Id from the Gateway's Geo Table after 180 seconds of inactivity.
        with self.Geo_table_dict_lock:
            for edx in self.Geo_table_dict['Enddevice']:
                idx = self.Geo_table_dict['Enddevice'].index(edx)
                if (time() - self.Geo_table_dict['Time'][idx]) > 180:
                    if self.LOG:
                        info(f"End-device ID: {edx} incative for more than 180 seconds.")
                    if self.DEBUG_:
                        print(f"End-device ID: {edx} incative for more than 180 seconds.")
                    del self.Geo_table_dict['Enddevice'][idx]
                    del self.Geo_table_dict['Rssi'][idx]
                    del self.Geo_table_dict['Time'][idx]
                    if self.LOG:
                        info(f"End-device ID: {edx} removed from the Gateway's Geo-Table.")
                    if self.DEBUG_:
                        print(f"End-device ID: {edx} removed from the Gateway's Geo-Table.")

    def send_data_G2H(self, socket_to_habitat, msg) -> bool:
    # Function to send data through socket.
        try:
            if self.LOG:
                debug(f"Trying to send the msg to Habitat: {msg}")
            encoded_msg = str(msg).encode(self.FORMAT)
            msg_length = len(encoded_msg)
            send_length = str(msg_length).encode(self.FORMAT)
            send_length += b' ' * (self.HEADER - len(send_length))
            socket_to_habitat.sendall(send_length)
            socket_to_habitat.sendall(encoded_msg)            
        except Exception as e:
            if self.LOG:
                error(f"Got this error in sending data to Habitat: {e}")
            if self.DEBUG_:
                print(f"Got this error in sending data to Habitat: {e}")
            return False
        else:
            if self.LOG:
                debug(f"Successfully sent the msg to Habitat: {msg}")
            if self.DEBUG_:
                print(f"Successfully sent the msg to Habitat: {msg}")
            return True
    
    def receive_Lora_pckts(self) -> tuple:
    # Function to receive pckts from Dragino over LoRa.
        try:
            if self.LOG:
                debug("Trying to receive from Dragino over LoRa.")        
            self.Dragino_Lora.available()
            lora_pckt_recv = self.Dragino_Lora.recv()
            with self.time_correction_lock:
                lora_pckt_recv_time = time() + self.time_correction
            lora_pckt_rssi = str(self.Dragino_Lora.rssi())            
        except Exception as e:
            if self.LOG:
                error(f"Error in receive_Lora_pckts: {e}")
            if self.DEBUG_:
                print(f"Error in receive_Lora_pckts: {e}")
            return None, None, None
        else:
            if lora_pckt_recv:
                if self.LOG:
                    debug(f"Received this pckt over LoRa: {lora_pckt_recv} and returning tuple of {lora_pckt_recv}, {lora_pckt_rssi}, {lora_pckt_recv_time}")                
                # Return LoRa pckt, pckt Rssi, pckt receive time.
                return lora_pckt_recv, lora_pckt_rssi, lora_pckt_recv_time
            else:
                if self.LOG:
                    debug("Didn't receive a pckt over LoRa, returning tuple of None, None, None")
                return None, None, None
    
    def parse_LoRa_packet(self, pckt, rssi, pckt_time) -> tuple:
    # Function to parse over the received LoRa packet.
    # returns str to save and str to send to Habitat in a tuple.       
        try:
            if self.LOG:
                debug(f"Trying to read the pckt as a dictionary: {pckt}")
            L = ''.join(chr(i) for i in pckt)
            data = literal_eval(L)                       
        except Exception as e:
            if self.LOG:
                error(f"Error in reading the received LoRa pckt as a dictionary: {e}")
            if self.DEBUG_:
                print(f"Error in reading the received LoRa pckt as a dictionary: {e}")            
            return None, None
        else:
            try:
                if data['Type']=='B':
                    try:
                        if self.LOG:
                            debug(f"Received a beacon pckt over LoRa, trying to parse over it: {data}")                        
                        self.Led_High(self.LoRa_packet_LED)
                        data['RSSI'] =  rssi 
                        save_dict = str({'Time':str(pckt_time),'Type':'B','ID':data['ID'],'RSSI':rssi,'Message':'-','Packetno.':'-','Mode':'E2G'})
                        self.store_ID(data)
                    except Exception as e:
                        if self.LOG:
                            error(f"Error in parsing over the beacon pckt received over LoRa: {e}") 
                        if self.DEBUG_:
                            print(f"Error in parsing over the beacon pckt: {e}")
                        self.Led_Low(self.LoRa_packet_LED)
                        return None, None
                    else:
                        if self.LOG:
                            info(f"Successfully parsed over the beacon packet received over LoRa. {data}") 
                        self.Led_Low(self.LoRa_packet_LED)
                        return save_dict, None
                elif data['Type']=='D':
                    try:
                        if self.LOG:
                            debug(f"Received a data pckt over Lora, trying to parse over it: {data}") 
                        self.Led_High(self.LoRa_packet_LED)
                        data['RSSI'] =  rssi 
                        save_dict = str({'Time':str(pckt_time),'Type':'D','ID':data['ID'],'RSSI':rssi,'Message':data['Message'],'Packetno.':data['Packetno.'],'Mode':'E2G'})
                        msg_to_H = str({'ID':data['ID'],'Message':data['Message'],'Packetno.':data['Packetno.']})
                        with self.from_lora_lock:
                            self.from_lora.append(msg_to_H)                        
                        self.store_ID(data)
                    except Exception as e:
                        if self.LOG:
                            error(f"Error in parsing over the data pckt received over LoRa: {e}") 
                        if self.DEBUG_:
                            print(f"Error in parsing over the data pckt received over LoRa: {e}")
                        self.Led_Low(self.LoRa_packet_LED)
                        return None, None
                    else:
                        if self.LOG:
                            info(f"Successfully parsed over the over the data pckt received over LoRa : {data}") 
                        self.Led_Low(self.LoRa_packet_LED)
                        return save_dict, msg_to_H
                elif data['Type']=='N':
                    try:
                        if self.LOG:
                            debug(f"Received time synchronisation request pckt over LoRa, trying to parse over it : {data}")                         
                        self.Led_High(self.LoRa_packet_LED)
                        Correctiontime = pckt_time + 0.020
                        response = str({'Type':'N','Gateway_ID': self.Gateway_ID,'Correctiontime':str(Correctiontime),'recv_time':str(pckt_time), 'init_time':data['init_time'], 'ID':data['ID']})
                        self.Dragino_Lora.send(self.Dragino_Lora.str_to_data(response)) 
                        self.Dragino_Lora.wait_packet_sent()                        
                    except Exception as e:
                        if self.LOG:
                            error(f"Error in parsing over the time synchronisation request pckt received over LoRa: {e}") 
                        if self.DEBUG_:
                            print(f"Error in parsing over the time synchronisation request pckt received over LoRa: {e}")
                        self.Led_Low(self.LoRa_packet_LED)
                        return None, None
                    else:
                        if self.LOG:
                            info(f"Successfully sent response: {response} for the time synchronisation pckt over LoRa.") 
                        self.Led_Low(self.LoRa_packet_LED)
                        return None, None                
            except Exception as e:
                if self.LOG:
                    error(f"Error in parsing over the LoRa pckt:{data} : {e}") 
                if self.DEBUG_:
                    print(f"Error in parsing over the LoRa pckt{data} : {e}")
                return None, None

    def create_conn_to_send_geo_table_to_H(self) -> bool:        
    # Create G2H connection to send the Gateway's Geo Table.
        self.geo_table_delta_time = time()
        if not len(self.g_sockets_outputs)>0:            
            Gateway_Client = socket(AF_INET, SOCK_STREAM)
            Gateway_Client.settimeout(1)
            if self.LOG:
                info("Connecting to Habitat to send the geo table.")
            if self.DEBUG_:
                print("Connecting to Habitat to send the geo table.")
            g2h_geo_ret = Gateway_Client.connect_ex((self.Habitat_ID, self.G2H_Port))
            if g2h_geo_ret == 0:
                if self.LOG:
                    info("Connected to Habitat to send the geo table.")  
                if self.DEBUG_:
                    print("Connected to Habitat to send the geo table.")              
                with self.g_sockets_outputs_list_lock and self.g_sockets_exceptions_list_lock:            
                    self.g_sockets_outputs.append(Gateway_Client)
                    self.g_sockets_exceptions.append(Gateway_Client)                           
            else:    
                if self.LOG:
                    error('Failed to connect to Habitat, to send the geo table!')
                if self.DEBUG_:
                    print('Failed to connect to Habitat, to send the geo table!')
                self.geo_table_delta_time = 0                
                return False   
        try:
            with self.geo_table_list_lock and self.Geo_table_dict_lock:
                self.geo_table_list.clear()                
                self.geo_table_list.append(self.Geo_table_dict)                
        except Exception as e:
            self.geo_table_delta_time = 0
            if self.LOG:
                error(f"Error in adding geo table to self.geo_table_list: {e}")
            if self.DEBUG_:
                print(f"Error in adding geo table to self.geo_table_list: {e}")
            return False
        else:
            return True         

    def create_conn_to_forward_lora_pckts_to_H(self) -> bool:        
    # Create G2H connection to send data.  
        if not len(self.g_sockets_outputs) > 0:            
            Gateway_Client = socket(AF_INET, SOCK_STREAM)
            Gateway_Client.settimeout(1)
            if self.LOG:
                info("Connecting to Habitat to forward the lora pckts.")
            if self.DEBUG_:
                print("Connecting to Habitat to forward the lora pckts.")
            g2h_lora_ret = Gateway_Client.connect_ex((self.Habitat_ID, self.G2H_Port))                
            if g2h_lora_ret == 0:
                if self.LOG:
                    debug("Connected to Habitat to forward the lora pckts.")
                if self.DEBUG_:
                    print("Connected to Habitat to forward the lora pckts.")
                with self.g_sockets_outputs_list_lock and self.g_sockets_exceptions_list_lock:                
                    self.g_sockets_outputs.append(Gateway_Client)
                    self.g_sockets_exceptions.append(Gateway_Client)                                            
                return True
            else:
                if self.LOG:
                    error('Failed to connect to Habitat, to forward the lora pckts!')  
                if self.DEBUG_:
                    print('Failed to connect to Habitat, to forward the lora pckts!')              
                return False


    #=== Select event loop functions ===#

    def g_sock_outputs_func(self, func_writeable) -> None:
    # Function to handle the output sockets.
        for g_sock in func_writeable: 
            if self.LOG:
                info("Writing on G2H pckt forwarding socket.")  
            if self.DEBUG_:
                print("Writing on G2H pckt forwarding socket.")

            if len(self.from_lora) > 0:
                self.Led_High(self.G2H_connection_LED) 
                with self.from_lora_lock:
                    # Loop to send all the pckts in self.from_lora to the Habitat.
                    p_h = 0
                    for i in range(0, len(self.from_lora)):
                        if not self.send_data_G2H(g_sock, self.from_lora[p_h]):
                            p_h+=1
                        else:
                            save_dict = literal_eval(self.from_lora[p_h])
                            with self.time_correction_lock:
                                save_data = str({'Time':str(time()+self.time_correction),'Type':'D','ID':save_dict['ID'],'RSSI':'-','Message':save_dict['Message'],'Packetno.':save_dict['Packetno.'],'Mode':'G2H'})
                            with self.e2h_file_lock:
                                self.save_data_to_file(self.test_result_e2h, save_data)
                            self.from_lora.pop(p_h)  
                            if self.LOG:
                                debug(f"Forwarded the lora pckts to Habitat successfully. {save_data}")
                            if self.DEBUG_:
                                print(f"Forwarded the lora pckts to Habitat successfully. {save_data}")
                            pass
                                                        
            if len(self.geo_table_list) > 0:                        
                self.Led_High(self.G2H_connection_LED) 
                self.Led_High(self.Geo_Table_update_LED)
                with self.geo_table_list_lock:
                    data_for_table = self.geo_table_list[0]
                    self.geo_table_list.clear()
                if self.send_data_G2H(g_sock, data_for_table):                            
                    self.geo_table_delta_time = time()                                
                    self.geo_table_success_delta_time = time()
                    if self.LOG:
                        debug("Sent table to Habitat successfully.")
                    if self.DEBUG_:
                        print("Sent table to Habitat successfully.")
                    pass
            
            self.send_data_G2H(g_sock, self.DISCONNECT_MESSAGE)          
            try:
                g_sock.shutdown(SHUT_RDWR)
                g_sock.close()                        
            except Exception as e:
                if self.LOG:
                    error(f"Error in closing the G2H socket @G: {e}")
                if self.DEBUG_:
                    print(f"Error in closing the G2H socket @G: {e}")
                with self.g_sockets_outputs_list_lock:
                    self.g_sockets_outputs.remove(g_sock)
                self.Led_Low(self.G2H_connection_LED)
                self.Led_Low(self.Geo_Table_update_LED)                
            else:
                with self.g_sockets_outputs_list_lock and self.g_sockets_exceptions_list_lock:
                    self.g_sockets_outputs.remove(g_sock)
                    self.g_sockets_exceptions.remove(g_sock)
                if self.LOG:
                    info("!!!CLOSED!!! G2H socket @G.")
                if self.DEBUG_:
                    print("!!!CLOSED!!! the G2H socket @G.")                
                self.Led_Low(self.G2H_connection_LED)
                self.Led_Low(self.Geo_Table_update_LED)        

    def g_sock_inputs_func(self, func_readable, func_G_server) -> None:
    # Function to handle the input sockets.
        for g_sock in func_readable:

            if g_sock is func_G_server:
                socket_from_Habitat, addr_g = func_G_server.accept()
                if self.LOG:                    
                    info(f"Receiving on H2G socket, Accepted connection from {addr_g}.")
                if self.DEBUG_:
                    print(f"Receiving on H2G socket, Accepted connection from {addr_g}.") 
                with self.g_sockets_inputs_list_lock and self.g_sockets_exceptions_list_lock:
                    self.g_sockets_inputs.append(socket_from_Habitat)
                    self.g_sockets_exceptions.append(socket_from_Habitat) 

            else:
                g_sock.settimeout(1)                       
                if self.LOG:
                    info("Receiving on H2G socket to forward data to end-device.")
                if self.DEBUG_:
                    print("Receiving on H2G socket to forward data to end-device.")
                try:                                   
                    msg_length = g_sock.recv(self.HEADER).decode(self.FORMAT)
                except Exception as e:
                    if self.LOG:
                        error(f"Error in h_sock readable @ msg_length = h_sock.recv : {e}")
                    try:
                        g_sock.shutdown(SHUT_RDWR)
                        g_sock.close()                                                
                    except Exception as e:
                        if self.LOG:
                            error(f"Error in closing the H2G socket @ G: {e}")
                        if self.DEBUG_:
                            print(f"Error in closing the H2G socket @ G: {e}")
                        with self.g_sockets_inputs_list_lock:
                            self.g_sockets_inputs.remove(g_sock)                        
                    else:
                        with self.g_sockets_inputs_list_lock and self.g_sockets_exceptions_list_lock:
                            self.g_sockets_inputs.remove(g_sock)
                            self.g_sockets_exceptions.remove(g_sock)
                        if self.LOG:                            
                            info("!!!CLOSED!!! the H2G socket @ G.")
                        if self.DEBUG_:
                            print("!!!CLOSED!!! the H2G socket @ G.")
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
                            pass
                            try:
                                g_sock.shutdown(SHUT_RDWR)
                                g_sock.close()                        
                            except Exception as e:
                                if self.LOG:
                                    error(f"Error in closing the H2G socket @ G: {e}")
                                if self.DEBUG_:
                                    print(f"Error in closing the H2G socket @ G: {e}")
                                with self.g_sockets_inputs_list_lock:
                                    self.g_sockets_inputs.remove(g_sock)  
                                self.Led_Low(self.G2H_connection_LED)                                                              
                            else:
                                with self.g_sockets_inputs_list_lock and self.g_sockets_exceptions_list_lock:
                                    self.g_sockets_inputs.remove(g_sock)
                                    self.g_sockets_exceptions.remove(g_sock)
                                if self.LOG:
                                    info("!!!CLOSED!!! the H2G socket @ G.")
                                if self.DEBUG_:
                                    print("!!!CLOSED!!! the H2G socket @ G.")
                                self.Led_Low(self.G2H_connection_LED)
                        else:
                            try:
                                data = g_sock.recv(msg_length).decode(self.FORMAT)   
                                if self.LOG:
                                    debug(f"Received message from Habitat: {data}")
                                if self.DEBUG_:
                                    print(f"Received message from Habitat: {data}")
                                if data == self.DISCONNECT_MESSAGE:                                                       
                                    try:
                                        g_sock.shutdown(SHUT_RDWR)
                                        g_sock.close()                        
                                    except Exception as e:
                                        if self.LOG:
                                            error(f"Error in closing the H2G socket @ G: {e}")
                                        if self.DEBUG_:
                                            print(f"Error in closing the H2G socket @ G: {e}")
                                        self.Led_Low(self.G2H_connection_LED)
                                    else:
                                        with self.g_sockets_inputs_list_lock and self.g_sockets_exceptions_list_lock:
                                            self.g_sockets_inputs.remove(g_sock)
                                            self.g_sockets_exceptions.remove(g_sock)
                                        if self.LOG:
                                            info("!!!CLOSED!!! the H2G socket @ G.")
                                        if self.DEBUG_:
                                            print("!!!CLOSED!!! the H2G socket @ G.")
                                        self.Led_Low(self.G2H_connection_LED)                                                            
                                else:
                                    try:
                                        data_dict = literal_eval(data)
                                    except Exception as e:
                                        if self.LOG:
                                            error(f"Error in reading the H2G data as dictionary: {e}")
                                        if self.DEBUG_:
                                            print(f"Error in reading the H2G data as dictionary: {e}")
                                            pass
                                    else:
                                        try:
                                            with self.time_correction_lock:
                                                save_dict = {'Time':str(time()+self.time_correction),'Mode':'H2G'}
                                            save_dict.update(data_dict)
                                            save_data = str(save_dict)
                                        except Exception as e:
                                            if self.LOG:
                                                error(f"Error in parsing over the dictionary pckt received from Habitat: {e}")
                                            if self.DEBUG_:
                                                print(f"Error in parsing over the dictionary pckt received from Habitat: {e}")
                                            pass
                                        else:
                                            with self.h2e_file_lock:
                                                self.save_data_to_file(self.test_result_h2e, save_data)
                                            with self.to_lora_lock:
                                                self.to_lora.append(data)
                                            if self.LOG:
                                                debug(f"Appended to to_lora: {data}")
                                            if self.DEBUG_:
                                                print(f"Appended to to_lora: {data}")
                                            pass  
                            except Exception as e:
                                if self.LOG:
                                    error(f"Error in h_sock readable @ data = g_sock.recv : {e}")
                                if self.DEBUG_:
                                    print(f"Error in h_sock readable @ data = g_sock.recv : {e}")                               
                                try:
                                    g_sock.shutdown(SHUT_RDWR)
                                    g_sock.close()                        
                                except Exception as e:
                                    if self.LOG:
                                        error(f"Error in closing the H2G socket @ G: {e}")
                                    if self.DEBUG_:
                                        print(f"Error in closing the H2G socket @ G: {e}")
                                    with self.g_sockets_inputs_list_lock:
                                        self.g_sockets_inputs.remove(g_sock)
                                    self.Led_Low(self.G2H_connection_LED)                                                                  
                                else:
                                    with self.g_sockets_inputs_list_lock and self.g_sockets_exceptions_list_lock:
                                        self.g_sockets_inputs.remove(g_sock)
                                        self.g_sockets_exceptions.remove(g_sock)
                                    if self.LOG:
                                        info("!!!CLOSED!!! the H2G socket @ G.")
                                    if self.DEBUG_:
                                        print("!!!CLOSED!!! the H2G socket @ G.")
                                    self.Led_Low(self.G2H_connection_LED)     

    def g_sock_exceptions_func(self, func_exceptions) -> None:
    # Function to handle the exceptions in the sockets.
        for g_sock in func_exceptions:
            if self.LOG:
                error("Exception in socket @G.")
            if self.DEBUG_:
                print("Exception in socket @G.")                                    
            with self.g_sockets_inputs_list_lock and self.g_sockets_exceptions_list_lock:
                try:
                    self.g_sockets_exceptions.remove(g_sock)
                    self.g_sockets_inputs.remove(g_sock)                    
                except Exception as e:
                    if self.LOG:
                        error(f"Error in removing socket from self.g_sockets_inputs_list in g_exceptional: {e}")
                    pass
            with self.g_sockets_outputs_list_lock and self.g_sockets_exceptions_list_lock:
                try:
                    self.g_sockets_exceptions.remove(g_sock)
                    self.g_sockets_outputs.remove(g_sock)                                            
                except Exception as e:
                    if self.LOG:
                        error(f"Error in removing socket from self.g_sockets_outputs_list in g_exceptional: {e}")
                    pass 
            try:
                g_sock.shutdown(SHUT_RDWR)
                g_sock.close()                        
            except Exception as e:
                if self.LOG:
                    error(f"Error in closing the socket @ G: {e}")
                if self.DEBUG_:
                    print(f"Error in closing the socket @ G: {e}")
                self.Led_Low(self.G2H_connection_LED) 
            else:
                if self.LOG:
                    debug(f"!!!CLOSED!!! the socket @ G.")
                if self.DEBUG_:
                    print(f"!!!CLOSED!!! the socket @ G.") 
                self.Led_Low(self.G2H_connection_LED)       

    def select_event_loop_handler_func(self) -> None:     
    # Select Event Loop handler function.
        G_server = G_server = create_server((self.Gateway_ID, self.H2G_Port), family = AF_INET, backlog = 5, reuse_port = True, dualstack_ipv6 = False)
        G_server.listen(5) 
        with self.g_sockets_inputs_list_lock and self.g_sockets_exceptions_list_lock:
            self.g_sockets_inputs.append(G_server)
            self.g_sockets_exceptions.append(G_server)
        
        while True: 

            if self.LOG:
                debug("Waiting in the select event loop handler.")   
            if self.DEBUG_:
                print("Waiting in the select event loop handler.")         
            with self.g_sockets_inputs_list_lock and self.g_sockets_outputs_list_lock and self.g_sockets_exceptions_list_lock:
                g_readable,g_writeable,g_exceptional = select(self.g_sockets_inputs,self.g_sockets_outputs,self.g_sockets_exceptions,1)            
            if self.LOG:
                debug("Got something from the select in the select_event_loop_handler.")   
            if self.DEBUG_:
                print("Got something from the select in the select_event_loop_handler.")              
            
            g_sock_outputs_thread = Thread(target=self.g_sock_outputs_func, args=(g_writeable,))
            g_sock_outputs_thread.start()
        
            g_sock_inputs_thread = Thread(target=self.g_sock_inputs_func, args=(g_readable, G_server))
            g_sock_inputs_thread.start()            
        
            g_sock_exceptions_thread = Thread(target=self.g_sock_exceptions_func, args=(g_exceptional,))                                                            
            g_sock_exceptions_thread.start() 

            g_sock_outputs_thread.join()
            g_sock_inputs_thread.join()
            g_sock_exceptions_thread.join()          
            
            self.get_thread_number()  
    
    def select_event_loop_thread(self) -> None:
    # Function to start the select event loop thread.
        event_loop_thread = Thread(target=self.select_event_loop_handler_func, args=())
        event_loop_thread.daemon = True 
        event_loop_thread.start()


    #=== H2E functions ===#    
    
    def to_enddevice(self, message) -> bool:
    # Function to send data from Gateway to the End-device over LoRa.
        try:
            if self.LOG:
                debug(f"Trying to send data to end-device over LoRa: {message}")
            self.Led_High(self.LoRa_packet_LED)
            data_dict = literal_eval(message)
            # Store H2E Multihop test data
            with self.time_correction_lock:
                save_dict = {'Time':str(time()+self.time_correction),'Mode':'G2E'}
            save_dict.update(data_dict)
            save_data = str(save_dict)
            with self.h2e_file_lock:
                self.save_data_to_file(self.test_result_h2e,save_data)
            self.Dragino_Lora.send(self.Dragino_Lora.str_to_data(message))
            self.Dragino_Lora.wait_packet_sent()            
        except Exception as e:
            if self.LOG:
                error(f"Error in sending data to End-device over LoRa: {e}")
            if self.DEBUG_:
                print(f"Error in sending data to End-device over LoRa: {e}")
            self.Led_Low(self.LoRa_packet_LED)
            return False
        else:
            if self.LOG:
                debug(f"Sent to End-device: {message}")
            if self.DEBUG_:
                print(f"Sent to End-device: {message}")
            self.Led_Low(self.LoRa_packet_LED)
            return True   

    def get_thread_number(self) -> None:
    # Function to get the number of threads running, and quit if less than 2.
        if active_count() < 2:
            if self.LOG:
                critical(f"Current running thread numbers = {active_count()}, hence quiting.")
            if self.DEBUG_:
                print(f"Current running thread numbers = {active_count()}, hence quiting.")
            GPIO.output(self.Gateway_Time_LED, GPIO.HIGH)
            GPIO.output(self.G2H_connection_LED, GPIO.HIGH)
            GPIO.output(self.Geo_Table_update_LED, GPIO.HIGH)
            GPIO.output(self.LoRa_packet_LED, GPIO.HIGH)
            quit(1)