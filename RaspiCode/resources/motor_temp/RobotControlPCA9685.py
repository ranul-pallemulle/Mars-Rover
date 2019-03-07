#!/usr/bin/env python
# coding: latin-1
# Autor:   Ingmar Stapel
# Translator: Shaun Gan (lol)
# Datum:   20160731
# Version:   2.0
# Homepage:   http://custom-build-robots.com
# Dieses Programm ist das sogenannte Steuerprogramm fuer das Roboter
# Auto ueber die Konsole und Tastatur vom PC aus.


# Es werden verschiedene Python Klassen importiert deren Funktionen
# im Programm benoetigt werden fuer die Programmverarbeitung.
import sys
import tty
import termios
import os
import readchar

# Das Programm L298NHBridge.py wird als Modul geladen. Es stellt
# die Funktionen fuer die Steuerung der H-Bruecke zur Verfuegung.
import L298NHBridgePCA9685 as HBridge

# Variablen Definition der linken und rechten Geschwindigkeit der
# Motoren des Roboter-Autos.
speedleft = 0
speedright = 0

# Das Menue fuer den Anwender wenn er das Programm ausfuehrt.
# Das Menue erklaert mit welchen Tasten das Auto gesteuert wird.
print("w/s: Forward")
print("a/d: Turn")
print("q:   Stop the Motors")
print("x:   Exit Program")

# Die Funktion getch() nimmt die Tastatureingabe des Anwenders
# entgegen. Die gedrueckten Buchstaben werden eingelesen. Sie werden
# benoetigt um die Richtung und Geschwindigkeit des Roboter-Autos
# festlegen zu koennen.


class Wheel_Motors:

   def __init__(self):
      pass

   def get_values(self, values):

   def


def getch():
   ch = readchar.readchar()
   return ch

# Die Funktion printscreen() gibt immer das aktuelle Menue aus
# sowie die Geschwindigkeit der linken und rechten Motoren wenn
# es aufgerufen wird.


def printscreen():
   # der Befehl os.system('clear') leert den Bildschirmihalt vor
   # jeder Aktualisierung der Anzeige. So bleibt das Menue stehen
   # und die Bildschirmanzeige im Terminal Fenster steht still.
   os.system('clear')
   print("w/s: Forward")
   print("a/d: Turn")
   print("q:   Stop the Motors")
   print("x:   Exit Program")
   print("========== Speedometer ==========")
   print("Speed of Left Motor:  ", speedleft)
   print("Speed of Right Motor: ", speedright)


# Program will not terminate until use presses x.
while True:
   # getch reads the character input by the user and performs the
   # appropriate movement.
   char = getch()

   # Das Roboter-Auto faehrt vorwaerts wenn der Anwender die
   # Taste "w" drueckt.
   if(char == "w"):
      # Robot accelerates in 10% increments, everytime w
      # has been pressed.
      speedleft = speedleft + 0.1
      speedright = speedright + 0.1

      if speedleft > 1:
         speedleft = 1
      if speedright > 1:
         speedright = 1
      # HBridge program, which was imported at the start,
      # transfers the speed to the left and right motors.
      HBridge.setMotorLeft(speedleft)
      HBridge.setMotorRight(speedright)
      printscreen()

   # Das Roboter-Auto faehrt rueckwaerts wenn die Taste "s"
   # gedrueckt wird.
   if(char == "s"):
      # das Roboter-Auto bremst in Schritten von 10%
      # mit jedem Tastendruck des Buchstaben "s" bis maximal
      # -100%. Dann faehrt es maximal schnell rueckwaerts.
      speedleft = speedleft - 0.1
      speedright = speedright - 0.1

      if speedleft < -1:
         speedleft = -1
      if speedright < -1:
         speedright = -1

      # Dem Programm L298NHBridge welches zu beginn
      # importiert wurde wird die Geschwindigkeit fuer
      # die linken und rechten Motoren uebergeben.
      HBridge.setMotorLeft(speedleft)
      HBridge.setMotorRight(speedright)
      printscreen()

    # mit dem druecken der Taste "q" werden die Motoren angehalten
   if(char == "q"):
      speedleft = 0
      speedright = 0
      HBridge.setMotorLeft(speedleft)
      HBridge.setMotorRight(speedright)
      printscreen()

   # Mit der Taste "d" lenkt das Auto nach rechts bis die max/min
   # Geschwindigkeit der linken und rechten Motoren erreicht ist.
   if(char == "d"):
      speedright = speedright - 0.1
      speedleft = speedleft + 0.1

      if speedright < -1:
         speedright = -1

      if speedleft > 1:
         speedleft = 1

      HBridge.setMotorLeft(speedleft)
      HBridge.setMotorRight(speedright)
      printscreen()

   # Mit der Taste "a" lenkt das Auto nach links bis die max/min
   # Geschwindigkeit der linken und rechten Motoren erreicht ist.
   if(char == "a"):
      speedleft = speedleft - 0.1
      speedright = speedright + 0.1

      if speedleft < -1:
         speedleft = -1

      if speedright > 1:
         speedright = 1

      HBridge.setMotorLeft(speedleft)
      HBridge.setMotorRight(speedright)
      printscreen()

   # The "x" key stops the endless loop and terminates the program
   # as well. Finally, the function exit () is called which stops
   # the motors.
   if(char == "x"):
      HBridge.setMotorLeft(0)
      HBridge.setMotorRight(0)
      HBridge.exit()
      print("Program Ended")
      break

   # The variable char is emptied per loop pass. This is necessary
   # to clean up further input.
   char = ""

# Ende des Programmes
