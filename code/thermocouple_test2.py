import board
import busio
import digitalio
import adafruit_max31856
#import ThermocoupleType 
import time
# create a spi object
spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)


# allocate a CS pin and set the direction
cs = digitalio.DigitalInOut(board.D0)
cs.direction = digitalio.Direction.OUTPUT

cs1 = digitalio.DigitalInOut(board.D5)
cs.direction = digitalio.Direction.OUTPUT

# create a thermocouple object with the above
#thermocouple = adafruit_max31856.MAX31856(spi, cs)

#typeJ = ThermocoupleType.J 
# print the temperature!

try: 
	i = 0
	while True:
		thermocouple = adafruit_max31856.MAX31856(spi, cs)
		temp = thermocouple.temperature * (9/5) + 32
		time.sleep(0.25)
		thermo2 = adafruit_max31856.MAX31856(spi,cs1)
		temp2 = thermo2.temperature * (9/5) + 32

		print(temp,' thermo J cycle',i)
		print(temp2, 'thermo K cycle',i)
		i+=1
		time.sleep(0.5)

except KeyboardInterrupt:
	print('done')
