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
global Temp_J
global Temp_K
global Probe_J
global Probe_K

global SPI_EN_J
global SPI_EN_K

global spi


#-------------------------------------------------------
def initThermo():

	global Temp_J
	global Temp_K
	global Probe_J
	global Probe_K

	global SPI_EN_J
	global SPI_EN_K

	global spi

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
#	i = 0


def writeTemp(csv_write):
        #Write temperature to CSV file
        global Temp_J
        global Temp_K
        timeStamp="{0}".format(time.strftime("%Y-%m-%d %H:%M:%S"))
        writer = csv_write
        writer.writerow([str(Temp_J) + '        ' ,str( Temp_K),"               "+ str( timeStamp)+ '   '])
        print('write successful')
        return


def readOut(writer):
	global Temp_K
	global Temp_J
	global Temp_K
	global Probe_J
	global Probe_K
	global SPI_EN_J
	global SPI_EN_K
	global spi

	try:
		#while True:
		#Temperatures are converted into Farenheit
		initThermo()

		Temp_J = Probe_J.temperature * (9/5) + 32
		time.sleep(0.25)
		Temp_K = Probe_K.temperature * (9/5) + 32

		#print('cycle',i)
		print ('Temperature of Type J Thermocouple:', Temp_J, 'F')
		print ('Temperature of Type K Thermocouple:', Temp_K, 'F')
		time.sleep(0.5)
		#i+=1
		writeTemp(writer)
		return

	except KeyboardInterrupt:
		print()
		print('Program Terminated')
		GPIO.cleanup()

def main(readIn):
	initThermo()
	readOut(readIn)


