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

Pressure_Transducer = digitalio.DigitalInOut(board.D8) #Pin BCM24, GPIO8, SPI0_CE0_N

AO_pin = 0

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


def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
#        GPIO.output(cspin, True)

        cspin.direction = digitalio.Direction.OUTPUT
        cspin.value = True  

#        GPIO.output(clockpin, False)  # start clock low

        clockpin.direction = digitalio.Direction.OUTPUT
        clockpin.value = False

#       GPIO.output(cspin, False)     # bring CS low
        cspin.value = True

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
#                        GPIO.output(mosipin, True)
                        mosipin.direction = digitalio.Direction.OUTPUT
                        mosipin.value = True

                else:
#                        GPIO.output(mosipin, False)
                        mosipin.direction = digitalio.Direction.OUTPUT
                        mosipin.value = False


                commandout <<= 1

#                GPIO.output(clockpin, True)
                clockpin.value = True

#                GPIO.output(clockpin, False)
                clockpin.value = True


        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
#                GPIO.output(clockpin, True)
#                GPIO.output(clockpin, False)
                clockpin.value = True
                clockpin.value = False

                adcout <<= 1
                if ( misopin.value ):
                        adcout |= 0x1

#        GPIO.output(cspin, True)
        cspin.value = True


        adcout >>= 1       # first bit is 'null' so drop it
        return adcout


def readTemp():
	#Temperatures are converted into Farenheit
	Temp_J = Probe_J.temperature * (9/5) + 32
	time.sleep(0.25)
	Temp_K = Probe_K.temperature * (9/5) + 32
	print ('Temperature of Type J Thermocouple:', Temp_J, 'F')
	print ('Temperature of Type K Thermocouple:', Temp_K, 'F')
	time.sleep(0.25)
	return


def main():
	k = 1
#	init()
	while True:
		print('****************')
		print('cycle',k)

		ad_value = readadc(AO_pin, board.SCLK, board.MOSI, board.MISO, Pressure_Transducer)
		voltage= ad_value*(3.3/1024)*5
		pressure = ( ( (voltage - 0.13)*(2000-0) ) / (16.5-0.13)  ) + 0.13
		time.sleep(0.5)
		print( "Voltage is: " + str("%.2f"%voltage)+"V")
		print( "Pressure is: " + str("%.2f"%pressure)+"V")
		readTemp()
		time.sleep(0.5)
		k+=1

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print()
		print('Program Terminated')
		GPIO.cleanup()

