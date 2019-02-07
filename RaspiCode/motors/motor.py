"""
I think the issue is perhaps hardware/ pluggin things into the wrong places/ motor might be a bit old. I AM NOT TOO SURE
"""

import sys
import time
import RPi.GPIO as GPIO


mode = GPIO.getmode()
GPIO.cleanup()

forward_PIN = 16
backward_PIN = 18
sleeptime = 1

GPIO.setmode(GPIO.BOARD)
GPIO.setup(forward_PIN,GPIO.OUT)
GPIO.setup(backward_PIN,GPIO.OUT)


def forward(x):

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(forward_PIN,GPIO.OUT)
    GPIO.output(forward_PIN,GPIO.HIGH)
    time.sleep(x)
    GPIO.output(forward_PIN, GPIO.LOW)

GPIO.cleanup()

forward(5)
