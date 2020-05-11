#This is the code that drives the Honeywell ABH pressure sensor that 
#has been run through a signal conditioner and an MCP3008 ADC IC chip

#libraries
import time as clk
import os
import RPi.GPIO as GPIO
import sys
import Adafruit_DHT
import sqlite3 as sql

#GPIO init
GPIO.setmode(GPIO.BCM)


