from time import sleep

import Adafruit_ADS1x15 as adf
adc = adf.ADS1115()

# Gain = 2/3 for reading voltages from 0 to 6.144V
# Gain = 1 for up to 4.096V
# See table 3 in ADS1115 datasheet
GAIN = 1

def read_adc_channel(channel):
    # Read ADC channel
    value = adc.read_adc(channel, gain=GAIN)
    volts = value / 65536.0 * 4.096
    return ((.89 - volts) * 100) / (.89 - .26)
    

# Main loop.
while True:
    # Read ADC channel 0
    for i in range(0..2):
        print(i)