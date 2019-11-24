import re

from abc import ABCMeta, abstractmethod
from org.joda.time import DateTime, Minutes, Seconds

from personal.intelliswitch.logging import getLogger, LogException

try:
	from personal.intelliswitch.astro import AstroSunInfo
	from personal.intelliswitch.base import BaseCore
	from personal.intelliswitch.criteria import BaseCriteria, BinaryCriteria
	from personal.intelliswitch.oh import isItemBinaryType, isItemOnOffType, isItemOpenClosedType, getOpenHABItem
	from personal.intelliswitch.service import RequiredServiceEnum
	
	from personal.intelliswitch.utils import getClassName, getDateToday, ParseTimeStringToDate
	
except:
	LogException()

try:
	from personal.intelliswitch import script as custom_scripts
except:
	LogException()



class ConditionManager(BaseCore):
	__metaclass__ = ABCMeta	
	
	def __init__(self):
		try:
			BaseCore.__init__(self, "")
			self.conditions = []
		except:
			LogException()
	
	def isActive(self):
		
		try:
			
			getLogger().debug("ConditionManager - Evaluating all conditions")
			#Loops through all conditions, if no conditions then always return True
			for curCondition in self.conditions:
				getLogger().debug("ConditionManager - Condition '" + curCondition.getName() + "' has value '" + str(curCondition.isActive()) + "'")
				if (curCondition.isActive()==False):
					return False
			return True
		except:
			LogException()
			
		return False

			
	def Add(self, arrConditions):
		try:

			for current in arrConditions:
				isValid = False
				curCondition = current
				
				if (isinstance(curCondition, basestring)):
					if (isItemBinaryType(curCondition)):
						condition = BinaryCriteria.CreateInstance(curCondition)
						curCondition = condition
						self.conditions.append( condition )
						isValid = True
				
				#TODO:: Do check if it supports conditions?
				elif (isinstance(curCondition, BaseCriteria)):
					self.conditions.append( curCondition )
					isValid = True

				if (isValid==False):
					getLogger().error("Invalid condition added to ConditionManager. A string must refer to either a 'OnOff' or a 'OpenClosed' Item in openHAB (Condition='" + str(curCondition) + "')")
					return False
					
				getLogger().debug(("Condition '{}' added to ConditionManager.").format(curCondition.getName()))
					
				
		except:
			LogException()
		
	def __retr__(self):
		return ("Class: '{}'".format(str(self.conditions)))

		
# ################################################
#
#	TimeOfDay Conditions (Day / Night)
#
# ################################################
		
class TimeOfDayCondition(BaseCriteria):
	__metaclass__ = ABCMeta	

	@abstractmethod
	def __init__(self):
		BaseCriteria.__init__(self, "")
	
	def getName(self):
		return getClassName(self)
		
	def getRequiredServices(self):
		return list(set(BaseCriteria.getRequiredServices(self) + [RequiredServiceEnum.ASTRO]))

		

class ActiveNightCondition(TimeOfDayCondition):
	__metaclass__ = ABCMeta	

	
	def __init__(self):
		self._arrSunInfo = None
		TimeOfDayCondition.__init__(self)
	
	
	def EventHandler_ServiceDataUpdated(self, serviceId, data):
		try:
			if (serviceId == RequiredServiceEnum.ASTRO) and (data is not None):
				getLogger().debug("Astro data arrived")
				if (isinstance(data[0], AstroSunInfo)) and (isinstance(data[1], AstroSunInfo)) and (isinstance(data[2], AstroSunInfo)):
					getLogger().debug(("'[ActiveNightCondition]' - Service data received for '{}'").format(serviceId))
					self._arrSunInfo = data
					getLogger().debug(("'[ActiveNightCondition]' - SunInfo Yesterday: '{}' - '{}'").format(self._arrSunInfo[0].getSunriseStart(), self._arrSunInfo[0].getSunriseEnd(), self._arrSunInfo[0].getSunsetStart(), self._arrSunInfo[0].getSunsetEnd()))
					getLogger().debug(("'[ActiveNightCondition]' - SunInfo Today    : '{}' - '{}'").format(self._arrSunInfo[1].getSunriseStart(), self._arrSunInfo[1].getSunriseEnd(), self._arrSunInfo[1].getSunsetStart(), self._arrSunInfo[1].getSunsetEnd()))
					getLogger().debug(("'[ActiveNightCondition]' - SunInfo Tomorrow : '{}' - '{}'").format(self._arrSunInfo[2].getSunriseStart(), self._arrSunInfo[2].getSunriseEnd(), self._arrSunInfo[2].getSunsetStart(), self._arrSunInfo[2].getSunsetEnd()))
				else:
					getLogger().debug("Astro data is not valid.")
			else:
				getLogger().warn(("'[ActiveNightCondition]' - Service data received for '{}' was not valid. Data: '{}'").format(serviceId, data))
		except:
			LogException()
			
	def isActive(self):

		try:
			curDateTime = DateTime()
			
			if (self._arrSunInfo is not None):
				sunInfoYesterday = self._arrSunInfo[0]
				sunInfoToday = self._arrSunInfo[1]
				sunInfoTomorrow = self._arrSunInfo[2]
				
				#After Sunset yesterday, Before sunrise Today -> Night
				if (curDateTime.isAfter(sunInfoYesterday.getSunsetStart()) and curDateTime.isBefore(sunInfoToday.getSunriseEnd())):
					getLogger().debug(("NIGHT -> '{}' is between '{}' - '{}'").format(curDateTime, sunInfoYesterday.getSunsetStart(), sunInfoToday.getSunriseEnd()))
					return True

				#After Sunrise today, Before sunset Today -> Day
				if (curDateTime.isAfter(sunInfoToday.getSunriseEnd()) and curDateTime.isBefore(sunInfoToday.getSunsetStart())):
					getLogger().debug(("DAY -> '{}' is between '{}' - '{}'").format(curDateTime, sunInfoToday.getSunriseEnd(), sunInfoToday.getSunsetStart()))
					return False
				
				#After Sunset today, Before Sunrise Tomorrow -> Night
				elif (curDateTime.isAfter(sunInfoToday.getSunsetStart()) and curDateTime.isBefore(sunInfoTomorrow.getSunriseEnd())):
					getLogger().debug(("NIGHT -> '{}' is between '{}' - '{}'").format(curDateTime, sunInfoToday.getSunsetStart(), sunInfoTomorrow.getSunriseEnd()))
					return True
					
				getLogger().warn(("'{}' didn't evalute night/day '{}', '{}', '{}', '{}'").format(curDateTime, sunInfoYesterday.getSunsetStart(), sunInfoToday.getSunriseEnd(), sunInfoToday.getSunsetStart(), sunInfoTomorrow.getSunriseEnd()))
			else:
				getLogger().warn("No SunInfo data found - Evaluating 'False'")
			return False
		except:
			LogException()
		
		return False
			

		
# ################################################
#
#	TimeSchedule Conditions
#
# ################################################
				
class TimeScheduleCondition(BaseCriteria):
	__metaclass__ = ABCMeta	

	def __init__(self, arrTimeInterval):
		try:
			self._schedules = arrTimeInterval
			BaseCriteria.__init__(self, "")
			#TODO:: Validate if all intervals actual is a TimeInterval
		except:
			LogException()		

	def getRequiredServices(self):
		return BaseCriteria.getRequiredServices(self)

		
	def isActive(self):
		try:
			
		
			for idx in range(len(self._schedules)):
					curInterval = self._schedules[idx]
					if (curInterval.isIntervalActive()):
						getLogger().debug("TimeScheduleCondition 'isActive()' evaluates 'True'")
						return True
		except:
			LogException()
		getLogger().debug("TimeScheduleCondition 'isActive()' evaluates 'False'")
		return False
	
	def __retr__(self):
		return str(self._schedules)



class BaseDateTimeInterval(BaseCore):
	__metaclass__ = ABCMeta	
	
	@abstractmethod
	def __init__(self, begin, end):
		try:
			self._begin = begin
			self._end = end
			
			BaseCore.__init__(self, "")
		except:
			LogException()		
	
	def getStartTime(self):
		return self._begin

	def getEndTime(self):
		return self._end

	#TODO:: Make a method that returns valid patterns as an array instead, and then make this a core function
	@abstractmethod
	def validateDateTimeString(self, name, dateTimeString):
			pass
			
	@abstractmethod
	def isIntervalActive(self):
		pass
		
	def __retr__(self):
		return "['" + str(self._begin) + "', '" + self._end + "']"		
		

		
class TimeInterval(BaseDateTimeInterval):

	__metaclass__ = ABCMeta	

	def __init__(self, begin, end):
		try:
			BaseDateTimeInterval.__init__(self, begin, end)
		except:
			LogException()		
	

	def validateDateTimeString(self, name, timeString):
		valid = False
		try:
			_pattern = re.compile("^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d))$")		
			if (inputString==self.SUNRISE):
				valid = True

			elif (inputString==self.SUNSET):
				valid = True	

			elif (self._pattern.match(inputString)):
				#if (self._pattern.match(inputString)):
				valid = True

		except:
			LogException()		
		return valid

		
	def isIntervalActive(self):
		try:
			strBeginTime = self.getStartTime()		
			strEndTime = self.getEndTime()
			dateToday = getDateToday()
			curTime = DateTime()
			
			calculatedStartTime = ParseTimeStringToDate(dateToday, self._begin)
			calculatedEndTime = ParseTimeStringToDate(dateToday, self._end)
					
			#End is before start -> interval is over midnight
			if calculatedEndTime.isBefore(calculatedStartTime):
				if (curTime.isAfter(calculatedStartTime)):
					calculatedEndTime = calculatedEndTime.plusDays(1)
				
				elif (curTime.isBefore(calculatedEndTime)):
					calculatedStartTime = calculatedStartTime.minusDays(1)
				
				else:
					calculatedEndTime = calculatedEndTime.plusDays(1)
				
			getLogger().debug(("Processing interval '{}' - '{}' -> '{}' - '{}'  - Current Time '{}', isActive='{}'").format(self.getStartTime(), self.getEndTime(), calculatedStartTime, calculatedEndTime, curTime, (curTime.isAfter(calculatedStartTime) and curTime.isBefore(calculatedEndTime))))
				
			return (curTime.isAfter(calculatedStartTime) and curTime.isBefore(calculatedEndTime))

		except:
			LogException()

		return False

# ################################################
#
#	Sequence Conditions
#
# ################################################
				
class SequenceCondition(BaseCriteria):
	__metaclass__ = ABCMeta	
	
	def __init__(self, objRule, duration, arrSequences):
		try:
			
			BaseCriteria.__init__(self, "")
			#TODO:: Might want to improve this a bit. The sequence will then be controlled on when oh is started
			self._sequenceBaseTimestamp = DateTime()
			self._sequenceDuration = duration
			self._dictSequences = {}
			self._objRule = objRule
			
			
			for curSequence in arrSequences:
				if (curSequence.getName() not in self._dictSequences):
					self._dictSequences[curSequence.getName()] = [curSequence]
				else:
					self._dictSequences[curSequence.getName()].append(curSequence)
					
					
			#TODO:: Validate if all sequences is a SequenceItem
		except:
			LogException()		

	def getRequiredServices(self):
		return BaseCriteria.getRequiredServices(self)

		
	def isActive(self):
		try:
			getLogger().info(("Calling 'isActive()' for '{}'").format(self.getName()))
			#diff = Minutes.minutesBetween(self._sequenceBaseTimestamp, DateTime()) 
			#curOffset = diff.getMinutes()
			activate = False

			diff = Seconds.secondsBetween( self._sequenceBaseTimestamp, DateTime())
			curOffset = diff.getSeconds()
			if (curOffset > self._sequenceDuration):
				self._sequenceBaseTimestamp = DateTime()
				curOffset = 0
			
			
			for curSwitchKey, actSequence in self._dictSequences.iteritems():
				#actSequence = self._dictSequences[curSwitchKey]
				activate = self._evaluateViritualSwitch(curOffset, actSequence)
				
				curVirtualSwitch = self._objRule.getVirtualSwitchByName(curSwitchKey)				
				getLogger().info(("About to evaluate state of '{}':  curState='{}' newState='{}'").format(curVirtualSwitch.getName(), curVirtualSwitch.isActive(), activate))

				#If state is wrong -> update
				if (((curVirtualSwitch.isActive()==True) and (activate == False)) or 
					((curVirtualSwitch.isActive()== False) and (activate==True))):
					
					getLogger().info(("Change state of '{}' from '{}' to '{}'").format(curVirtualSwitch.getName(), curVirtualSwitch.isActive(), activate))
					curVirtualSwitch.updateState(activate)
		except:
			LogException()
		
		return False


	def _evaluateViritualSwitch(self, curOffset, actSequence):
		activate = False
		getLogger().info(("_evaluateViritualSwitch: actSequence='{}' curOffset='{}'").format(actSequence, curOffset))

		try:
			for curSequence in actSequence:
				getLogger().info(("Evaluate sequence '{}'  (begin='{}' end='{}', curOffset='{}')").format(curSequence.getName(), curSequence.getBeginOffset(), curSequence.getEndOffset(), curOffset))
			
				if ((curSequence.getBeginOffset() <= curOffset) and (curOffset<curSequence.getEndOffset())):
					getLogger().debug(("  Light '{}' is ACTIVE").format(curSequence.getName()))
					activate = True
					break
				else:
					getLogger().debug(("  Light '{}' is INACTIVE").format(curSequence.getName()))
		except:
			LogException()
		finally:		
			getLogger().info(("_evaluateViritualSwitch: DONE! activate='{}'").format(activate))
			
		return activate
		
	def __retr__(self):
		return str(self._schedules)


# ################################################
#
#	TimeOfDay Conditions (Day / Night)
#
# ################################################
		
class ScriptCondition(BaseCriteria):
	__metaclass__ = ABCMeta	


	def __init__(self):
		BaseCriteria.__init__(self, "")
	
	def getName(self):
		return getClassName(self)
		
	def getRequiredServices(self):
		return list(set(BaseCriteria.getRequiredServices(self)))
		
		
	def __init__(self, methodName):
		self._methodName = methodName
		BaseCriteria.__init__(self, "")
	
	
	def EventHandler_ServiceDataUpdated(self, serviceId, data):
		pass
	
	
	def doesMethodExist(self):
		try:
			if self._methodName in dir(custom_scripts):
				return True
		except:
			LogException()
		return False

		
	def isActive(self):
		try:
			if (self.doesMethodExist()):
				return bool( getattr(custom_scripts, self._methodName)() )
			else:
				logger.error("The method '{}' is not defined in the file 'personal.intelliswitch.script.py'".format(self._methodName))
		except:
			LogException()
		
		return False
			
'''
def doesItemSupportOneOf(itemName, types=[]):
	curItem = getOpenHABItem(itemName)
	if (len(list(set(curItem.getAcceptedDataTypes()) & set(types)))>0):
		return True
	return False


'''