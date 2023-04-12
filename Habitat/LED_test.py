import RPi.GPIO as GPIO
from time import sleep

DEBUG = True  # Set True to Debug the software.

# use BOARD numbering for LEDs and rf95.
GPIO.setmode(GPIO.BOARD)

GPIO.setup(13, GPIO.OUT) # small red LED
GPIO.setup(15, GPIO.OUT) # white LED
GPIO.setup(16, GPIO.OUT) # red LED
GPIO.setup(18, GPIO.OUT) # yellow LED

GPIO.output(13, GPIO.LOW)
GPIO.output(15, GPIO.LOW)
GPIO.output(16, GPIO.LOW)
GPIO.output(18, GPIO.LOW)

print("Testing LEDs...")

def Led_High(led):
    GPIO.output(led, GPIO.HIGH)

def Led_Low(led):
    GPIO.output(led, GPIO.LOW)
    
while True:
    Led_High(13)
    sleep(0.3)
    Led_Low(13)
    Led_High(16)
    sleep(0.3)
    Led_Low(16)
    Led_High(18)
    sleep(0.3)
    Led_Low(18)
    Led_High(15)
    sleep(0.3)
    Led_Low(15)