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
import csv
import sqlite3 as sql
from voltage import *
from thermocouple import *

#Global Variables
#-------------------------------------------------------
#Chip Select Pins

SPI_EN_J = digitalio.DigitalInOut(board.D0) #Pin BCM0/Pin ID_SD on GPIO Extenstion Board

SPI_EN_K =  digitalio.DigitalInOut(board.D5) #Pin BCM5/GPIO Extension Board

Pressure_Transducer = digitalio.DigitalInOut(board.D8) #Pin BCM24, GPIO8, SPI0_CE0_N

AO_pin = 2

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

#Pressure Calibration
minVoltage = 1.74 #Derived from testing
maxVoltage = 5.0  #Derived from Signal Conditioner setting

minPressure = 0
maxPressure = 2000

def writeTemp(csv_write):
	#Write temperature to CSV file
	global Temp_J
	global Temp_K
	timeStamp="{0}".format(time.strftime("%Y-%m-%d %H:%M:%S"))
	writer = csv_write
	writer.writerow([str(Temp_J) + '	' ,str( Temp_K),"		"+ str( timeStamp)+ '	'])
	print('write successful')

def readTemp(csv_write):
	global Temp_J
	global Temp_K
	#Temperatures are converted into Farenheit
	Temp_J = round(Probe_J.temperature * (9/5) + 32,2)
#	time.sleep(0.25)
	Temp_K = round(Probe_K.temperature * (9/5) + 32,2)
	print ('Temperature of Type J Thermocouple:', Temp_J, 'F')
	print ('Temperature of Type K Thermocouple:', Temp_K, 'F')
#	time.sleep(0.25)

	writeTemp(csv_write)

	return


def main():
	k = 1
	print('Program Initializing')
	time.sleep(2)
	print('Program Start')
	try:
		con = sql.connect('dataLog.db')
		cur = con.cursor()
		cur.execute( '''
		 CREATE TABLE IF NOT EXISTS "dataLog" ( 
		"timestamp" TEXT,
		"tempJ" TEXT,
		"tempK" TEXT,
		"Pressure" TEXT,
		"Viscosity" TEXTL
			)
	 	''')
		with open("tempLog.csv","w") as log:
			writer = csv.writer(log)
			writer.writerow(['Tpye J	','Type K','	Time Recorded	'])
			while True:

				print('****************')
				print('cycle',k)

				print(' ')
				voltage  = round(mainRead(),2)
				print(' ')

				time.sleep(1)
				pressure = ( ((voltage - minVoltage)*(maxPressure-minPressure))/(maxVoltage-minVoltage)  )+minPressure

				print( "Pressure is: " + str("%.2f"%pressure) +" Psi")
				print(' ')

				viscosity = 0 #for testing purposes 
				time.sleep(1)

				readOut(writer)
#				readTemp(writer)

				timeIn ="{0}\n".format(time.strftime("Y-%m-%d %H:%M:%S"))
				cur.execute(''' INSERT INTO dataLog(timestamp,tempJ,tempK,Pressure,Viscosity) VALUES (?,?,?,?,?)''',(timeIn,Temp_J,Temp_K,pressure,viscosity))
				con.commit()
				print("successful write to db")
				time.sleep(1)
				k+=1
	except KeyboardInterrupt:
		pass
		GPIO.cleanup()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print()
		print('Program Terminated')
		GPIO.cleanup()
