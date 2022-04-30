import rf95

# Create rf95 object with CS0 and external interrupt on pin 25
lora = rf95.RF95(0, 25, 17)

if not lora.init(): # returns True if found
        print("RF95 not found")
        quit(1)
else:
        print("RF95 LoRa mode ok")

# set frequency, power and mode
lora.set_frequency(433.0)
lora.set_tx_power(5)
lora.set_modem_config(rf95.Bw125Cr45Sf128)
while True:
        # Wait until data is available
        while not lora.available():
                pass
        # Receive
        data = lora.recv()
        data1 = bytes(data)
        data2 = data1.decode('utf-8')
        print (data2)
