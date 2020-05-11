#!/usr/bin/env python
#Thermocouple.py
#This code is meant to drive the temperature measurement of the Type J and Type K thermocouples
#Readings are gathered using the Adafruit MAX31855 Breakout Boards

#Import Libraries
import time
import os
import adafruit_max31856 as maxBoard
import busio
import board
import spidev
import digitalio
import RPi.GPIO as GPIO
#Global Variables
#-------------------------------------------------------
#Chip Select Pins

SPI_EN_J = digitalio.DigitalInOut(board.D0) #Pin BCM0/Pin ID_SD on GPIO Extenstion Board

SPI_EN_K =  digitalio.DigitalInOut(board.D5) #Pin BCM5/GPIO Extension Board

#Initialize SPI

#SCLK = BCM11 MOSI=BCM10 MISO = BCM9
spi = busio.SPI(board.SCLK, board.MOSI, board.MISO) 

#Thermocouple Initialization via MMAX31856 Board
Probe_J = maxBoard.MAX31856(spi,SPI_EN_J) #Type J thermocouple --> outer block
Probe_K = maxBoard.MAX31856(spi,SPI_EN_K) #Type K thermocouple --> inner block

#Temperature Reading. Temperatures are recorded in Celsius by default
#------------------------------------------------------------------------
#Temperature Initialization
Temp_J = 0
Temp_K = 0
i = 0

try:
	while True:
		#Temperatures are converted into Farenheit
		Temp_J = Probe_J.temperature * (9/5) + 32
		time.sleep(0.25)
		Temp_K = Probe_K.temperature * (9/5) + 32

		print('cycle',i)
		print ('Temperature of Type J Thermocouple:', Temp_J, 'F')
		print ('Temperature of Type K Thermocouple:', Temp_K, 'F')
		time.sleep(0.5)
		i+=1

except KeyboardInterrupt:
	print()
	print('Program Terminated')
	GPIO.cleanup()

