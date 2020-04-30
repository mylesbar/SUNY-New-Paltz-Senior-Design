#!/usr/bin/env python
#Thermocouple.py
#This code is meant to drive the temperature measurement of the Type J and Type K thermocouples
#Readings are gathered using the Adafruit MAX31855 Breakout Boards

#Import Libraries
import time
import os
import Rpi.GPIO as GPIO
import adafruit_max31855 as maxBoard
import busio
import board

import spidev

#Globals & GPIO Pins

SPI_MOSI  = 9
SPI_MISO = 21
SPI_CLK = 23

SPI_EN_J = 24
SPI_EN_K = 26

#Initialize GPIO

GPIO.setmode(GPIO.BCM)

#Initialize SPI & Max31855 Board

spi = busio.SPI(SPI_CLK, SPI_MOSI, SPI_MISO)

Probe_J = maxBoard.MAX31855(spi,SPI_EN_J) #Type J thermocouple --> outer block
Probe_K = maxBoard.MAX31855(spi,SPI_EN_K) #Type K thermocouple --> inner block

#Temperature Reading. Temperatures are recorded in Celsius by default

Temp_J = 0
Temp_K = 0

try:
	while True:
		Temp_J = Probe_J.temperature
		Temp_K = Probe_K.temperature

		print ('Temperature of Type J Thermocouple:', Temp_J, 'C')
		print ('Temperature of Type K Thermocouple:', Temp_K, 'C')
		time.sleep(0.5)

except KeyboardInterrupt:
	print('Program Terminated')
	GPIO.cleanup()

