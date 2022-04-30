import rf95
import time
# Create rf95 object with CS0 and external interrupt on pin 25
lora = rf95.RF95(0, 25, 17)

if not lora.init(): # returns True if found
        print("RF95 not found")
        quit(1)
else:
        print("RF95 LoRa mode ok")
i = 0
# set frequency, power and mode
lora.set_frequency(433.0)
lora.set_tx_power(14)
lora.set_modem_config(rf95.Bw125Cr45Sf128)
while True:
        # Send some data
        data = "Hello "+ str(i)
        lora.send(lora.str_to_data(data))
        lora.wait_packet_sent()
        print(data)
        i +=1
        time.sleep(2)