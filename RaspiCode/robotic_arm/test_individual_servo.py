#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 18:41:35 2019

@author: ShaunGan
"""

import board
import busio
import adafruit_pca9685
from adafruit_servokit import ServoKit
import time as time
i2c = busio.I2C(board.SCL,board.SDA)

servo = adafruit_pca9685.PCA9685(i2c)
kit = ServoKit(channels=16)

PIN = int(input("Which servo would you like to test?: \n:Bottom - 12\n:Middle - 13 \n:Grabber - 14 \n"))

kit.servo[PIN].set_pulse_width_range(600,2500)

if PIN == 12:
    for i in range (5):
        kit.servo[PIN].angle = 45. * i
        print(45.*i)
        time.sleep(1)


elif PIN == 13:
    for i in range (5):
        kit.servo[PIN].angle = 22.5 * i
        print(22.5*i)
        time.sleep(1)
    
elif PIN == 14:
    test = None
    for i in range (5):
        if test == 1:
            value = 80
            kit.servo[PIN].angle = value
            print(value)
            test = 0
        else: 
            value = 0
            kit.servo[PIN].angle = value
            print(value)
            test = 1
        time.sleep(1.5)

else: 
    raise Exception("Please select a valid PIN Number")
