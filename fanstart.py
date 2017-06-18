import datetime
import threading

from flask import Flask
import os
from flask import render_template, redirect, url_for, request, session, flash, g
from functools import wraps
from DbClass import DbClass

#====Stepper and light sensor===
#forlightsensor
import spidev

import RPi.GPIO as GPIO
import time

spi = spidev.SpiDev()
spi.open(0, 0)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

ControlPin = [7,11,13,15]



print("Fan staat aan")

# ===Start fan=========
import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)

GPIO.setup(37, GPIO.OUT)

p = GPIO.PWM(37, 0.8)

p.start(0)

try:
    while True:
        print("loop")
        for i in range(100):
            p.ChangeDutyCycle(i)
            time.sleep(0.02)
        for i in range(100):
            p.ChangeDutyCycle(100 - i)
            time.sleep(0.02)

except KeyboardInterrupt:
    pass

p.stop()

GPIO.cleanup()