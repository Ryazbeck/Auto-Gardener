from time import sleep

import Adafruit_ADS1x15 as adf
adc = adf.ADS1115()

# Gain = 2/3 for reading voltages from 0 to 6.144V
# Gain = 1 for up to 4.096V
# See table 3 in ADS1115 datasheet
GAIN = 1

# Main loop.
while True:
    # Read ADC channel 0
    value = adc.read_adc(1, gain=GAIN)
    volts = value / 65536.0 * 4.096
    moisture_percent = ((.89 - volts) * 100) / (.89 - .26)
    print(f"{int(moisture_percent)}%")
    
    sleep(.5)