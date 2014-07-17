#!/usr/bin/python

import time
import sys

colourMap = {"off":"000", "red":"200", "green":"020", "blue":"002", "cyan":"022", "white":"111", "warmwhite":"222", "purple":"102", "magenta":"202", "yellow":"220", "orange":"210"}

class Event:
	def __init__(self, name):
		self.name = name
		self.steady = ColourSteady()
		self.blink = ColourBlink()
	def initiate(self,shade, pattern, duration, blinkrate):
		if pattern == "steady":
			self.steady.change(shade, duration)
		elif pattern == "blink":
			self.blink.change(shade, duration, blinkrate)
		else:
			print "no pattern specified. Use either 'steady' or 'blink'"

class ColourSteady:
	def __init__(self):
		self.name = "steady"
	def change(self, shade, duration):

		start = int(time.time())
		timeout = start
		timeout = int(time.time()) - timeout
		
		while int(duration) >= timeout:
			ledBorgColour = colourMap[shade]
			ledBorg = open('/dev/ledborg', 'w')
			ledBorg.write(ledBorgColour)
			ledBorg.close()
			timeout = int(time.time()) - start
			time.sleep(0.5)
			
		self.shade = "off"
		ledBorgColour = colourMap[self.shade]
		ledBorg = open('/dev/ledborg', 'w')
		ledBorg.write(ledBorgColour)
		ledBorg.close()

class ColourBlink:
	def __init__(self):
		self.name = "blink"
	def change(self, shade, duration, blinkrate):
	
		start = int(time.time())
		timeout = start
		timeout = int(time.time()) - timeout

		while int(duration) >= timeout:		
			ledBorgColour = colourMap[shade]
			ledBorg = open('/dev/ledborg', 'w')
			ledBorg.write(ledBorgColour)
			ledBorg.close()
			
			time.sleep(float(blinkrate))
			self.shade = "off"
			ledBorgColour = colourMap[self.shade]
			ledBorg = open('/dev/ledborg', 'w')
			ledBorg.write(ledBorgColour)
			ledBorg.close()
			timeout = int(time.time()) - start
			time.sleep(float(blinkrate))
		
		self.shade = "off"
		ledBorgColour = colourMap[self.shade]
		ledBorg = open('/dev/ledborg', 'w')
		ledBorg.write(ledBorgColour)
		ledBorg.close()

#TODO create the triggers based on various world events such as - new email, weather, rail, etc)

test = Event("test")
test.initiate("magenta", "blink", "30", "0.75")

