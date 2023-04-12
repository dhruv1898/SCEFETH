#! /usr/bin/python3

# Author: Eenesh Chavan


### IMPORTING LIBRARIES SPACE ###

from Gateways import Gateway
from time import time

# Create Gateway object.
Gateway_ = Gateway(5, 0, 22, 11, 13, 15, 16, 18, False, True)

e2h_file, h2e_file = Gateway_.Test_files()

# wait till time not synchronized.
while not Gateway_.G_time_synced:
    Gateway_.Time_Sync()

# Initialize Gateway.
Gateway_.initialized = True

# start the select thread for sending and receiving the data from the sockets.
Gateway_.select_event_loop_thread()

while True:    

    # Loop to run when Gateway's time is synced with Habitat.
    if Gateway_.initialized:
        
        # send packets to End-device over LoRa.
        if len(Gateway_.to_lora) > 0:
            with Gateway_.to_lora_lock:
                p_l = 0              
                for i in range(0, len(Gateway_.to_lora)):
                    if not Gateway_.to_enddevice(Gateway_.to_lora[p_l]):
                        p_l+=1
                    else:
                        Gateway_.to_lora.pop(p_l)   
        else:    
            # Receive from LoRa if no pckts to send over LoRa.        
            LoRa_pckt, LoRa_pckt_rssi, LoRa_pckt_time = Gateway_.receive_Lora_pckts()        
            # if any pckt received over LoRa, save and add to from_lora list.
            if LoRa_pckt:
                save_str_dict, msg_2_Habitat = Gateway_.parse_LoRa_packet(LoRa_pckt, LoRa_pckt_rssi, LoRa_pckt_time)
                if save_str_dict:
                    with Gateway_.e2h_file_lock:
                        Gateway_.save_data_to_file(e2h_file, save_str_dict)
                   
        # send Geo_table to Habitat every 30 seconds.
        if (time() - Gateway_.geo_table_delta_time >= 30):              
            Gateway_.create_conn_to_send_geo_table_to_H()                 
        else:
            # if any pckt in from_lora list and,
            # no socket in use for G2H then send all pckts in from_lora to Habitat.
            if Gateway_.from_lora:            
                Gateway_.create_conn_to_forward_lora_pckts_to_H()        

    # Try every 180 seconds to remove the End-device Id from the Gateway's Geo Table after 180 seconds of inactivity.
    if time() - Gateway_.check_ID_delta_time >= 180:
        Gateway_.check_ID_time()
        Gateway_.check_ID_delta_time = time()

    # Synchronize time every 3600 seconds and if last talk to Habitat was more than 120 seconds ago.
    if (time()-Gateway_.G_when_time_synced >= 3600) or (time() - Gateway_.geo_table_success_delta_time >= 120):
        Gateway_.Led_Low(Gateway_.Gateway_Time_LED)
        Gateway_.geo_table_success_delta_time = time()
        Gateway_.G_time_synced = False        
        if Gateway_.DEBUG:
            print("Lost synchronization with Habitat.")

    # Time synchronization with Habitat.
    if not Gateway_.G_time_synced:
        Gateway_.Time_Sync()
    
    Gateway_.get_thread_number()