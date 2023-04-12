#!!! CHANGE ID in 1 place only, at line number 21. !!!#

from time import sleep, ticks_ms
#from machine import Pin
# from onewire import DS18X20
# from onewire import OneWire
import socket
from machine import SD
import os
from network import LoRa
import mpy_decimal
import pycom


pycom.heartbeat(False)

while True:

    print(ticks_ms()/1000)