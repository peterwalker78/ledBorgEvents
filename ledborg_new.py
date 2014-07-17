#!/usr/bin/python

import time
import imaplib
import re
import urllib2
import datetime
from xml.dom import minidom
from bs4 import BeautifulSoup

loopTime = "300"
colourMap = {"off":"000", "red":"200", "green":"020", "blue":"002", "cyan":"022", "white":"111", "warmwhite":"222", "purple":"102", "magenta":"202", "yellow":"220", "orange":"210"}

def set_col(col):
	colour = colourMap[col]
#	print colour
	ledBorg = open('/dev/ledborg', 'w')
	ledBorg.write(colour)
	ledBorg.close()
	print "the LED is " + str(col)

class GmailAlert:
	def __init__(self):
		self.name = "Gmail Alert"
	def should_fire(self):
		try:
			conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
			conn.login("user", "pass")
			unreadCount = re.search("UNSEEN (\d+)", conn.status("INBOX", "(UNSEEN)")[1][0]).group(1)
			print "Number of unread emails is " + unreadCount
			return int(unreadCount) > int("6")
		except:
			print "Unable to retreive email stats"
		
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

class AlertHandler:
	def __init__(self):
		self.alerts = []
		self.gmail = GmailAlert()
		self.weather = WeatherAlert()
		self.rail = RailAlert()
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
	def set_led(self):
		if self.gmail in self.alerts:
			set_col("red")
			time.sleep(10)
		if self.weather in self.alerts:
			set_col("blue")
			time.sleep(10)
		if self.rail in self.alerts:
			set_col("purple")
			time.sleep(10)

	def clear_alerts(self):
		self.alerts = []
		print self.alerts
			
try:
	while True:
		ah = AlertHandler()
		ah.active_alerts()
		finish_time = datetime.datetime.now() + datetime.timedelta(seconds=int(loopTime))
		ft = str(finish_time)
		
		if not ah.alerts:
			print "No active alerts.. sleeping until " + ft[11:19]
			while datetime.datetime.now() < finish_time:
				time.sleep(30)
				print "Still sleeping.. waking up at " + ft[11:19]
		else:
			print "Cycling through alerts until " + ft[11:19]
			while datetime.datetime.now() < finish_time:
				ah.set_led()

		for x in range (0,4):
			set_col("off")
			time.sleep(0.1)
			set_col("yellow")
			time.sleep(0.1)
		set_col("off")
		ah.clear_alerts()

except KeyboardInterrupt:
	print "\nKeyboard interrupt detected. Quitting."

finally:
	set_col("off")
