#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 18:23:20 2019

@author: ShaunGan

There are two ways to approach this, one through PCA9685, the other through the 
GPIO library. I don't really know the difference and as to which is better
for this purposes of the project. 
"""

from PCA9685 import PWM #(?)
import RPi.GPIO as GPIO
#import smbus
#import time

# for RPI version 1, use "bus = smbus.SMBus(0)"
#bus = smbus.SMbus(1)
#
##Slave Address 1
#address_1 = 0x01
##Slave Address 2
#address_2 = 0x02

#not sure how to set up the slave address
SERVO_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT) # (pin number x6 for 6 motors)
GPIO.setwarnings(False)


#Number of Motors
n_motors = 6

#servo = GPIO.PWM(SERVO_PIN,GPIO.OUT)
#servo.start(0)
##Do we use BUS or PWM? to set the values. 

class motor:
    def __init__(self):
        
        pass
    
    def set_speed(self,values = None):
        """
        Loops through different motors and changes the duty cycle for each motor
        """
        for i in range (n_motors):
            motor_i = PWM(17+i) #probablye different gpio outputs
            motor_i.set_duty_cycle(percent = values)
#            servo.ChangeDutyCycle(values) 
    
    def read_speed(self):
        speed = bus.read_byte_data(address,1)
        return speed
        
    def stop_motor(self,values = None):
        for i in range (n_motors):
            motor_i = PWM(17+i)
            motor_i.set_duty_cycle(percent = 0)    
            


#def set_duty_cycle(self,values):
#    pwm.set_duty_cycle(values)
#    print(values)
            
            
#TODO
#set speed left set speed right. 
#have a function called set_values to get the values. 

