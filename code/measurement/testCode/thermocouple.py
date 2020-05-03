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
import sqlite3 as sql
import sys
import csv

#Global Variables
#-------------------------------------------------------
#Chip Select Pins

SPI_EN_J = digitalio.DigitalInOut(board.D5) #Pin BCM0/Pin ID_SD on GPIO Extenstion Board

SPI_EN_K =  digitalio.DigitalInOut(board.D0) #Pin BCM5/GPIO Extension Board

#Initialize SPI

#SCLK = BCM11 MOSI=BCM10 MISO = BCM9
spi = busio.SPI(board.SCLK, board.MOSI, board.MISO) 

#Thermocouple Initialization via MMAX31856 Board
Probe_J = maxBoard.MAX31856(spi,SPI_EN_J) #Type J thermocouple --> outer block
Probe_K = maxBoard.MAX31856(spi,SPI_EN_K) #Type K thermocouple --> inner block

#Temperature Reading. Temperatures are recorded in Celsius by default
#------------------------------------------------------------------------
#Temperature Initialization
global Temp_J
global Temp_K
i = 0

def recordTemp():
	#Temperatures are converted into Farenheit
	global Temp_J
	global Temp_K
	Temp_J =round( Probe_J.temperature * (9/5) + 32,5)
	time.sleep(0.25)
	Temp_K = round(Probe_K.temperature * (9/5) + 32,5)


def printTemp():
	#Print temperatures to console
	global Temp_K
	global Temp_J
	print ('Temperature of Type J Thermocouple:', Temp_J, 'F')
	print ('Temperature of Type K Thermocouple:', Temp_K, 'F')

def writeTemp(csv_write):
	#Write temperature to CSV file
	global Temp_J
	global Temp_K
	timeStamp="{0}".format(time.strftime("%Y-%m-%d %H:%M:%S"))
	writer = csv_write
	writer.writerow([str(Temp_J) + '	' ,str( Temp_K) + '		',str( timeStamp)+ '	'])
	print('write successful')
try:

	con = sql.connect('..tempLog.db') #connect to database
	cur = con.cursor()		  #set cursor
	cur.exectute('''
	CREATE TABLE IF NOT EXISTS "tempLog" (
	"timestamp" TEXT,
	"temp_J" TEXT,
	"temp_K" TEXT
		)
	''')

	with open("tempLog.csv","w") as log:
		writer = csv.writer(log)
		writer.writerow(['Tpye J Thermocouple	','Type K Thermocouple		','Time Recorded	'])
		while True:
			print('cycle',i)
			recordTemp()
			printTemp()
			writeTemp(writer)
			time.sleep(0.5)
			i+=1

except KeyboardInterrupt:
	print()
	print('Program Terminated')
	GPIO.cleanup()

