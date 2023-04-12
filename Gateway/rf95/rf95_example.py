import rf95
from time import sleep
# Create rf95 object with CS0 and external interrupt on pin 25
lora = rf95.RF95(0, 22, 11)

if not lora.init(): # returns True if found
	print("RF95 not found")
	quit(1)
else:
	print("RF95 LoRa mode ok")

# set frequency, power and mode
lora.set_frequency(868.5)
lora.set_tx_power(5)
lora.set_modem_config(rf95.Bw125Cr45Sf128)

print(f"mode of rf95 is: {lora.mode}")
# Send some data
lora.send([0x00, 0x01, 0x02, 0x03])
print(f"mode of rf95 is: {lora.mode}")
print(f"sent this: {[0x00, 0x01, 0x02, 0x03]}")
lora.wait_packet_sent()
print("finished waiting 1")
print(f"mode of rf95 is: {lora.mode}")
# Send a string
lora.send(lora.str_to_data("$TELEMETRY TEST"))
print(f"mode of rf95 is: {lora.mode}")
print(f"sent this: {'$TELEMETRY TEST'}")
lora.wait_packet_sent()
print(f"mode of rf95 is: {lora.mode}")
print("finished waiting 2")

# Wait until data is available 
while not lora.available():
    sleep(1)
    print("done sleep 1")
    print(f"mode of rf95 is: {lora.mode}")
    print("waiting in available")
    print(f"mode of rf95 is: {lora.mode}")
    pass
# Receive
data = lora.recv()
print(data)
for i in data:
	print(chr(i), end="")
print()
lora.set_mode_idle()