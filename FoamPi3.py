import VL53L0X
import time,datetime,csv
import sys
from mcp9600 import MCP9600
import numpy


##############Setup for HX711######################

EMULATE_HX711=False

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()


#Set the pins for the HX711 ADC
hx = HX711(17, 27)

hx.set_reading_format("MSB", "MSB")

# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
#hx.set_reference_unit(113)

referenceUnit = -113
hx.set_reference_unit(referenceUnit)

hx.reset()
print("Taring Balance")
hx.tare()
print("Tare done")


# Create a VL53L0X object
tof = VL53L0X.VL53L0X(i2c_bus=1,i2c_address=0x29)
tof.open()
tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)

timing = tof.get_timing()
if timing < 20000:
    timing = 20000

#Code to calcualate the inital height between TOF laser and bottom of box

print("Getting zero Height value")

h0arr = []

for k in range(25):
    h0arr.append(tof.get_distance())

h0 = numpy.mean(h0arr)
print ('H0 = ' ,h0)

print("Zero Height Calculated: ",h0," mm")

print("")
CSVfile = input("Please enter your Filename: ")

t0 = datetime.datetime.now()

#Create Thermocouple object

mcp9600 = MCP9600(i2c_addr=0x60)
mcp9600.set_thermocouple_type('K')


#Create new CSV file
with open(CSVfile+'.csv','w') as CSVw:
    CSVwriter = csv.writer(CSVw)
    CSVwriter.writerow(['Time', 'Temp', 'Tj', 
                      'Distance','Mass'])
    
    try:
        while True:
        
            #Read all values from their appropriate objects
            t = datetime.datetime.now()
            tdiff = (t-t0).total_seconds()
            mass = hx.get_weight(3)
            distance = tof.get_distance()
            Hsave = h0 - distance
            temp = mcp9600.get_hot_junction_temperature()
            inttemp = mcp9600.get_cold_junction_temperature()
            
            #Prints the raw data
            print("t: ",tdiff," s")
            print("T: ",temp," C", "--Tj: ",inttemp," C")
            print("Distance:", distance," mm")
            print("Mass: ", mass," g")

            hx.power_down()
            hx.power_up()
            
            CSVwriter.writerow([tdiff, temp, inttemp, Hsave, mass])
        
            time.sleep(0.1)

    except(KeyboardInterrupt, SystemExit):
        tof.stop_ranging()
        tof.close()
        cleanAndExit()
        
