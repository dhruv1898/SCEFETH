#! /usr/bin/python3

# Author: Eenesh Chavan


### IMPORTING LIBRARIES SPACE ###

from Habitats import Habitat
from time import sleep

Habitat_ = Habitat(13, 15, 16, 18, False, True)

End_devices = ['ID001','ID002','ID003','ID004']

# Update the End-devices list @ Habitat.
Habitat_.update_Enddevices_at_Habitat(End_devices)

# create the test data files.
e2h_file, h2e_file = Habitat_.Test_files()

# start the select thread for sending and receiving the data from the sockets.
Habitat_.select_event_loop_thread()

h2epacketnumber = 0

while True:
    
    sleep(30) 

    for Node in End_devices:
        data_dict = {'Habitat':Habitat_.Habitat_ID,'ID':Node,'Payload':'Greetings from H','Packetno.':h2epacketnumber} 
        
        # get the Gateway list for sending data to the End-device.
        E_id, G_array = Habitat_.G_list_for_H2E(Node)

        if type(G_array) != type(None):
            # create a socket for sending the data to a Gateway from the G_array list.
            Habitat_.create_conn_to_G_for_H2E(E_id, G_array, data_dict)
        sleep(1) # This sleep is to prevent send burst of data from Habitat, or it interrupts receiving of packet at end-device.
    
    h2epacketnumber += 1

    Habitat_.get_thread_number()