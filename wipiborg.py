#!/usr/bin/python

# Import all necessary libraries
import time
import imaplib
import re
import urllib2
import datetime
from xml.dom import minidom
from bs4 import BeautifulSoup
import wiringpi2 as wiringpi
wiringpi.wiringPiSetup()

# Set up the GPIO pins
PIN_RED = 0
PIN_GREEN = 2
PIN_BLUE = 3
wiringpi.pinMode(PIN_RED, wiringpi.GPIO.OUTPUT)
wiringpi.pinMode(PIN_GREEN, wiringpi.GPIO.OUTPUT)
wiringpi.pinMode(PIN_BLUE, wiringpi.GPIO.OUTPUT)

# Set global variable to control sub loop durations
loopTime = "300"

# Set up the colour map to allow simple colour selection when called
colourMap = {"off":"000", "red":"100", "green":"010", "blue":"001", "yellow":"110", "cyan":"011", "magenta":"101", "white":"111"}

# Function to set the LED to the required colour
def set_col(col):
	colour = colourMap[col]
#	print colour[0]
#	print colour[1]
#	print colour[2]
# Logic to format passed in colour in the required way for SetLedBorg
	RVAL = int(colour[0])
	GVAL = int(colour[1])
	BVAL = int(colour[2])
# Logic to format passed in colour in the required way for SetLedBorg
	wiringpi.digitalWrite(PIN_RED, RVAL)
	wiringpi.digitalWrite(PIN_GREEN, GVAL)
	wiringpi.digitalWrite(PIN_BLUE, BVAL)
	print "the LED is " + str(col)

# Class for checking number of unread emails
class GmailAlert:
	def __init__(self):
		self.name = "Gmail Alert"
	def should_fire(self):
		try:
			conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
			conn.login("user", "pass")
			unreadCount = re.search("UNSEEN (\d+)", conn.status("INBOX", "(UNSEEN)")[1][0]).group(1)
			print "Number of unread emails is " + unreadCount
			return int(unreadCount) > int("5")
		except:
			print "Unable to retreive email stats"

# Class for check outside temperature		
class WeatherAlert:
	def __init__(self):
		self.name = "Weather Alert"
	def should_fire(self):
		try:
			url = "http://api.openweathermap.org/data/2.5/weather?q=hitchin&mode=xml"
			dom = minidom.parse(urllib2.urlopen(url))
			temperatures = dom.getElementsByTagName('temperature')
			temp = temperatures[0].attributes['value'].value
			tempC = float(temp) - 273
			print "The temperature is " + str(tempC) +"C"
			return float(tempC) < float("4")
		except:
			print "Unable to retreive weather information"

# Class for checking for rail disruptions		
class RailAlert:
	def __init__(self):
		self.name = "Rail Alert"
	def should_fire(self):
		try:
			soup = BeautifulSoup(urllib2.urlopen("http://www.journeycheck.com/firstcapitalconnect/route?from=HIT&to=KGX&action=search&savedRoute=#").read())
			soupdata = soup.find("div", id="headingTextTC")
			cancels = str(soupdata.text).splitlines()[1]
			print "The number of cancellations is " + str(cancels)
			return float(cancels) > float("0")
		except:
			print "Unable to retreive rail information"	 

# Main handler to call classes and chuck active alerts into an array
class AlertHandler:
	def __init__(self):
		self.alerts = []
		self.gmail = GmailAlert()
		self.weather = WeatherAlert()
		self.rail = RailAlert()
# Check the alerts
	def active_alerts(self):
		if not self.gmail in self.alerts:
			if self.gmail.should_fire():
				self.alerts.append(self.gmail)
		if not self.weather in self.alerts:
			if self.weather.should_fire():
				self.alerts.append(self.weather)					
		if not self.rail in self.alerts:
			if self.rail.should_fire():
				self.alerts.append(self.rail)
# Turn on the relevant LED colour
	def set_led(self):
		if self.gmail in self.alerts:
			set_col("red")
			time.sleep(5)
		if self.weather in self.alerts:
			set_col("blue")
			time.sleep(5)
		if self.rail in self.alerts:
			set_col("magenta")
			time.sleep(5)
# Clear the alerts from the array for next check
	def clear_alerts(self):
		self.alerts = []
		print self.alerts

# Main Programme loop			
try:
	while True:
		ah = AlertHandler()
		ah.active_alerts()
# Work out the time to finish sub loops
		finish_time = datetime.datetime.now() + datetime.timedelta(seconds=int(loopTime))
		ft = str(finish_time)
# Code to execute if there are no alerts in the array		
		if not ah.alerts:
			print "No active alerts.. sleeping until " + ft[11:19]
			while datetime.datetime.now() < finish_time:
# Flashes the LED periodically to show that the programme has not hung
				for x in range (0,5):
					set_col("off")
					time.sleep(0.05)
					set_col("yellow")
					time.sleep(0.05)
					set_col("off")
				print "Still sleeping.. waking up at " + ft[11:19]
				time.sleep(20)
# Code to execute if there are alerts in the array
		else:
			print "Cycling through alerts until " + ft[11:19]
			while datetime.datetime.now() < finish_time:
				ah.set_led()
# Clear the array for next pass
		ah.clear_alerts()

# Catch ctrl+c events
except KeyboardInterrupt:
	print "\nKeyboard interrupt detected. Quitting."

# Turn off the LED before the programme quits
finally:
	set_col("off")
