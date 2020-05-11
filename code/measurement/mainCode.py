#!/usr/bin/env python
#mainCode.py
#This is the testing method for calculating viscosity of wax in an injection cycle
#ALL VALUES ARE SIMULATED USING CONSTRAINTS FROM MPI SYSTEMS INC.'S MODEL 55 WAX INJECTOR

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
import random as ran
import pandas as pd
import math as mth
from voltage import *
from thermocouple import *
#Global Variables
i = 0 #To keep track of program cycle
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

#Pressure Calibration
minVoltage = 1.74 #Derived from testing
maxVoltage = 5.0  #Derived from Signal Conditioner setting

minPressure = 0
maxPressure = 2000

length_short = 2 #inches
length_long  = 3 #inches

capillary = 0.002 #2mm capillary chamber diameter
capillary_radius = 0.001 #1mm capillary radius


#Theoretical Inputs
P_Test_1 = ran.randint(0,1000) #Average Barrel Pressure Simulation through SHORT 2MM capilary. Measured in Psi
P_Test_2 = ran.randint(0,1000) #Average Barrel Pressure Simulation through LOMG 2MM capilary. Measured in Psi

flow_rate = 0.1 #units in cubic inches per second
slope = 0.6 #simulated value for derivation

P_minus = abs(P_Test_1 - P_Test_2) #Used to calculate Entryway Pressure Drop
A = ( P_minus / (1 + capillary) ) #Used to calculate Entryway Pressure Drop

Entry_drop = P_Test_1 - A

P_averaged = 800 #Simulated average value for testing. Measured in Psi
P_atmospheric = 97664 #Simulated value for Atmospheric pressure. Measured in Pascals @ 318ft above sea elevation & 21C

Delta_P = P_averaged - P_atmospheric  #Derivation for Shear Stress
velocity = flow_rate / ( mth.pi * mth.pow(capillary_radius,2) )

wall_shear_stress = ( (-Delta_P)*float(capillary/2) ) / (2 * length_short) #Simualtion calculated using short capilary

Y_apparent = ( 8 * velocity )/capillary

Real_Shear_Rate = Y_apparent * ( (3*slope+1) / (4 * slope) )

viscosity_measured = wall_shear_stress / Y_apparent

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
	print('Pressure P_test_1 is',str( P_Test_1) )
	print('Pressure P_test_2 is', str(P_Test_2) )
	print('measured viscosity is', str(viscosity_measured) )
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
		with open("dataLog.csv","w") as log:
			writer = csv.writer(log)
#			writer.writerow(['Pressure P_test_1 ', P_Test_1])
#			writer.writerow(['Pressure P_test_2 ', P_Test_2])
#			writer.writerow(['wall shear sterss ', wall_shear_stress])
#			writer.writerow(['Y_apparent shear strain ', Y_apparent])
#			writer.writerow(['calculated viscosity ', viscosity_measured])
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
#		read_file = pd.read_csv(r'dataLog.csv',error_bad_lines=False)
#		read_file.to_excel(r'tempLog.xlsx',index = None, header=True)
		pass
		GPIO.cleanup()
		print('Program Terminated')

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print()
		writer.writerow(['Pressure P_test_1 ', P_Test_1])
		writer.writerow(['Pressure P_test_2 ', P_Test_2])
		writer.writerow(['wall shear sterss ', wall_shear_stress])
		writer.writerow(['Y_apparent shear strain ', Y_apparent])
		writer.writerow(['calculated viscosity ', viscosity_measured])
		read_file = pd.read_csv(r'tempLog.csv')
		read_file.to_excel(r'tempLog.xlsx',index = None, header=True)
		print('Program Terminated')
		GPIO.cleanup()
