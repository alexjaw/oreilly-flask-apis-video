#!/usr/bin/env python
#
# Measures temperature using w1 sensor DS18B20
#
# http://www.electrokit.com/temperatursensor-vattentat-ds18b20.49197
# Connections: Black = GND, Red = VDD, White = Data
# rpi2 pinout
# http://www.jameco.com/Jameco/workshop/circuitnotes/raspberry-pi-circuit-note.html
# Connection to rpi
# http://www.reuk.co.uk/DS18B20-Temperature-Sensor-with-Raspberry-Pi.htm
# w1 data:
# ls -l /sys/bus/w1/devices/
# cat /sys/bus/w1/devices/28-000007a6f1c4/w1_slave
import datetime
import time

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('temperature.py')

#------------------------------------#
#               SETTINGS             #
#------------------------------------#

T_CALIBRATION = 0.0  # TODO: calibrate!
W1 = '/sys/bus/w1/devices/28-000007a6f1c4/w1_slave'

#------------------------------------#
#           END OF SETTING           #
#------------------------------------#


def _print_start_information():
    logger.info('---------- Starting temperature logger... ----------')
    logger.info('W1 sensor path = %s', W1)


def is_temp_ok(t):
    if T_MIN <= t and t <= T_MAX:
        return True
    else:
        return False


def get_data_from_hw():
    # This is directly communicationg with hardware
    try:
        with open(W1, 'r') as w1:
            data = w1.read()
        return data
    except Exception as e:
        raise


def get_temp_from_w1_data(data):
    # Returns float
    tmp = data.split('\n')[1].split(' ')[9]
    t = tmp.split('=')[1]
    temperature = float(t)/1000 - T_CALIBRATION
    return temperature


def measure_temp():
    try:
        data = get_data_from_hw()
    except Exception as e:
        raise
    temperature = get_temp_from_w1_data(data)
    return temperature


if __name__ == '__main__':
    logger.info('Temperature = %s', str(measure_temp()))
