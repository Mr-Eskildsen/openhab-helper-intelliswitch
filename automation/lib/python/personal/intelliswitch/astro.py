from abc import ABCMeta, abstractmethod

from org.joda.time import DateTime
from java.util import Calendar, Date

from personal.intelliswitch.logging import getLogger, LogException


#TODO:: This one fails on RPI (when API not installed)
#TODO:: USE This to verify if action is installed or not!
try:
	import core.actions as Actions
except:
	LogException()

class AstroSunInfo(object):
	def __init__(self, sunriseStart, sunriseEnd, sunsetStart, sunsetEnd):
		try:
			self._sunriseStart = AstroSunInfo.to_joda_datetime(sunriseStart)
			self._sunriseEnd = AstroSunInfo.to_joda_datetime(sunriseEnd)
			self._sunsetStart = AstroSunInfo.to_joda_datetime(sunsetStart)
			self._sunsetEnd = AstroSunInfo.to_joda_datetime(sunsetEnd)
		except:
			LogException()
			
			
	#TODO:: Move to convert module
	@classmethod
	def to_joda_datetime(cls, value):
		try:
			if isinstance(value, DateTime):
				return value
			
			calendar = AstroSunInfo.to_java_calendar(value)
		
			return DateTime(
				calendar.get(Calendar.YEAR),
				calendar.get(Calendar.MONTH) + 1,
				calendar.get(Calendar.DAY_OF_MONTH),
				calendar.get(Calendar.HOUR_OF_DAY),
				calendar.get(Calendar.MINUTE),
				calendar.get(Calendar.SECOND),
				calendar.get(Calendar.MILLISECOND),
				)
		except:
			LogException()
		
	#TODO:: Move to convert module
	@classmethod
	def to_java_calendar(cls, value):
		try:
			if isinstance(value, Calendar):
				return value
    
			if isinstance(value, datetime.datetime):
				c = Calendar.getInstance()
				c.set(Calendar.YEAR, value.year)
				c.set(Calendar.MONTH, value.month - 1)
				c.set(Calendar.DAY_OF_MONTH, value.day)
				c.set(Calendar.HOUR_OF_DAY, value.hour)
				c.set(Calendar.MINUTE, value.minute)
				c.set(Calendar.SECOND, value.second)
				c.set(Calendar.MILLISECOND, value.microsecond / 1000)
				return c

			if isinstance(value, Date):
				c = Calendar.getInstance()
				c.time = value
				return c
			
			if isinstance(value, DateTime):
				return value.toGregorianCalendar()
				
			if isinstance(value, DateTimeType):
				return value.calendar
		except:
			LogException()
	
	def getSunriseStart(self):
		return self._sunriseStart
		
	def getSunriseEnd(self):
		return self._sunriseEnd

	def getSunsetStart(self):
		return self._sunsetStart
	
	def getSunsetEnd(self):
		return self._sunsetEnd


		
def getAstroSunInfo(date, latitude, longitude):

	try:
		curDate = None
		if (date.__class__.__name__ == "Date"):
			curDate = date
		elif (date.__class__.__name__  == "DateTime"):
			curDate = date.toDate()

		strLatitude = str(latitude)			
		strLongitude = str(longitude)
		
		getLogger().debug("Calling Astro Action with date='{}' latitude='{}' longitude='{}'".format(curDate, strLatitude, strLongitude))
		sunriseStart = 	Actions.Astro.getAstroSunriseStart(curDate, float(strLatitude), float(strLongitude))
		sunriseEnd = 	Actions.Astro.getAstroSunriseEnd(curDate, float(strLatitude), float(strLongitude))
		sunsetStart = 	Actions.Astro.getAstroSunsetStart(curDate, float(strLatitude), float(strLongitude))
		sunsetEnd = 	Actions.Astro.getAstroSunsetEnd(curDate, float(strLatitude), float(strLongitude))
		asi = AstroSunInfo(sunriseStart, sunriseEnd, sunsetStart, sunsetEnd)
		getLogger().debug("Astro Action called with date='{}' returned Sunrise#Start='{}' Sunrise#End='{}' Sunset#Start='{}' Sunset#End='{}'".format(curDate, asi.getSunriseStart(), asi.getSunriseEnd(), asi.getSunsetStart(), asi.getSunsetEnd()))
		return asi 
	except:
		LogException()
