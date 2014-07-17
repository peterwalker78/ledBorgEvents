#!/usr/bin/python

import wiringpi2 as wiringpi
wiringpi.wiringPiSetup()
wiringpi.digitalWrite(0, 0)
wiringpi.digitalWrite(2, 0)
wiringpi.digitalWrite(3, 0)
print "the LED is off"
