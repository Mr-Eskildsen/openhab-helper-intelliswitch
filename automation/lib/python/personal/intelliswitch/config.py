from abc import ABCMeta, abstractmethod
#import uuid
#import traceback
from personal.intelliswitch.logging import LogException, getLogger

try:
	import core

	from personal.intelliswitch.condition import TimeInterval, ActiveNightCondition
	from personal.intelliswitch.location import Location
	from personal.intelliswitch.manager import RuleManager
	from personal.intelliswitch.output import DimmerOutput, SwitchOutput
	from personal.intelliswitch.rule import ScheduleRule, StateTriggerRule
except:
	LogException()



KEY_LOCATION = 'LOCATION'
KEY_MANAGERS = 'MANAGERS'
KEY_LATITUDE = 'latitude'
KEY_LONGITUDE = 'longitude'
KEY_RULETYPE='type'
KEY_TRIGGERS = 'TRIGGERS'
KEY_CONDITIONS = 'CONDITIONS'
KEY_SCHEDULES = 'SCHEDULES'
KEY_OUTPUTS = 'OUTPUTS'

## TODO:: THIS IS FOR DimmerOutput
KEY_ACTIVATED_VALUE = ''
KEY_DEACTIVATED_VALUE = ''


RULETYPE_TRIGGER= 'trigger'
RULETYPE_SCHEDULE= 'schedule'
KEY_RULES = 'RULES'
KEY_NAME = 'name'
KEY_DESCRIPTION = 'description'
KEY_LOGLEVEL = 'LOGGING_LEVEL'
LOGLEVEL_INFO = 'INFO'

KEY_BEGIN = 'begin'			
KEY_END = 'end'

KEY_DELAY = 'delay'
KEY_TIMEOUT = 'timeout'

KEY_TYPE = 'type'
VALUE_ITEM = 'item'
VALUE_CHECK = 'check'
VALUE_ACTIVENIGHT ='ActiveNight'


					
def hasConfigKey(cfg, key):
	if key in cfg:
		return True
	return False
	
#def getRequiredConfigValue(cfg, configKey, decode = False):	
#	if configKey not in cfg:
#		getLogger().error("Required config key '{}' not found in configuration".format(configKey))#
#		
#	return cfg[configKey].decode('utf8')
	

	
#TODO:: Improved fail handling to avoid floats ints etc to fail on decode
def getConfigValue(cfg, configKey, defaultValue = None, decode = False):	
	if (configKey not in cfg) and (defaultValue is not None):
		getLogger().error("Required config key '{}' not found in configuration".format(configKey))

	elif configKey in cfg:
		if decode:
			return cfg[configKey].decode('utf8')
		else:
			return cfg[configKey]
		
	return defaultValue

			
			
			
			
class IntelliSwitchManager(object):
	'''
	Provides IntelliSwitch main class that will load configuration
	'''

	def __init__(self):
		'''
		Initialise the IntelliSwitch class

		Expects:

		* Nothing really...
		'''
		
		self.__version__ = '0.2.0'
		self.__version_info__ = tuple([ int(num) for num in self.__version__.split('.')])
		#self.log = logging.getLogger("{}.personal.intelliswitch".format(LOG_PREFIX))
		getLogger().info(("Starting openHAB JSR223 library 'IntelliSwitch' Version '{}'").format(self.__version__))

		self.ruleManagers = []
		mgrNumber = 0

	def LoadConfig(self, configuration):
		self.loggingLevel = getConfigValue(configuration, KEY_LOGLEVEL, LOGLEVEL_INFO)

		#
		# Loading location
		# #############################
		location = None
		if hasConfigKey(configuration, KEY_LOCATION):
			# Load from JSR223 Configuration
			location = Location(lng = configuration[KEY_LOCATION][KEY_LONGITUDE], lat = configuration[KEY_LOCATION][KEY_LATITUDE])
			getLogger().info(("Loading location from configuration file: latitude='{}', longitude='{}'").format(location.getLatitude(), location.getLongitude()))
		else:
			# Load from openHAB System Configuration
			location = Location.FromSystemLocation()	
			if (location is not None):
				getLogger().info(("Loading location from openHAB System configuration (latitude='{}', longitude='{}')").format(location.getLatitude(), location.getLongitude()))
		
		# No location found -> Fail
		if (location is None):
			getLogger().error("Location is not set. Either set location in openHAB system settings, or set it in configuration")
			return False
	
		for i in range(len(configuration[KEY_MANAGERS])):
			getLogger().info("Processing manager configuration '{}'".format(configuration[KEY_MANAGERS][i]))
			mgrNumber = i+1
			cfgRuleMgr = configuration[KEY_MANAGERS][i]

			newRuleMgr = RuleManager(getConfigValue(cfgRuleMgr, KEY_NAME, decode=True), getConfigValue(cfgRuleMgr, KEY_DESCRIPTION, defaultValue='', decode=True), location)
			# Process each rule
			for j in range(len(cfgRuleMgr[KEY_RULES])):
				
				getLogger().info(u"Processing rule '{}' for manager '{}'".format(cfgRuleMgr[KEY_RULES][j], getConfigValue(cfgRuleMgr, KEY_NAME, decode=True)))
				cfgRule = cfgRuleMgr[KEY_RULES][j]
				rule_type = getConfigValue(cfgRule, KEY_RULETYPE,decode=True)
				
				if rule_type == RULETYPE_TRIGGER:
					newRuleObj = self.createTriggerRule(cfgRule)
				elif  rule_type == RULETYPE_SCHEDULE:
					newRuleObj = self.createScheduleRule(cfgRule)
				else:
					getLogger().error("Unknown rule type '{}' in configuration '{}'".format(rule_type, cfgRule))
					newRuleObj = None
					
				if newRuleObj is not None:
					newRuleMgr.Add(newRuleObj)
				
			newRuleMgr.Commit()
			self.ruleManagers.append(newRuleMgr)
            
	def processTriggers(self, ruleName, cfgTrigger):
		arrTriggers = []
		# Triggers
		for i in range(len(cfgTrigger)):
			arrTriggers.append(cfgTrigger[i])
		return arrTriggers

		
	def processSchedules(self, ruleName, cfgSchedule):
		arrSchedules = []
		# Schedules
		for i in range(len(cfgSchedule)):
			#getLogger().info(("Time interval: '{}' - '{}'").format(cfgSchedule[i][KEY_BEGIN], cfgSchedule[i][KEY_END]))
			arrSchedules.append(TimeInterval(cfgSchedule[i][KEY_BEGIN], cfgSchedule[i][KEY_END]))
		return arrSchedules
		
		
	def processConditions(self, ruleName, cfgConditions):
		arrConditions = []
		# Conditions
		for i in range(len(cfgConditions)):
			curItem = None
			getLogger().info("Processing Condition '{}'".format(cfgConditions[i]))
			#Complex node
			if hasConfigKey(cfgConditions[i], KEY_TYPE):
				if getConfigValue(cfgConditions[i], KEY_TYPE)== VALUE_ITEM:
					#TODO:: Might need to read more values here?
					curItem = getConfigValue(cfgConditions[i], KEY_NAME)
					
				elif getConfigValue(cfgConditions[i], KEY_TYPE)== VALUE_CHECK:
					if getConfigValue(cfgConditions[i], KEY_NAME)==VALUE_ACTIVENIGHT:
						getLogger().info("Creating 'ActiveNight Condition")
						curItem = ActiveNightCondition()
			# Just the name of an openHAB item
			else:
				curItem = cfgConditions[i]
			
			getLogger().debug("Condition is '{}'".format(curItem))
			if curItem is None:
				getLogger().error("Invalid configuration '{}'".format(cfgConditions[i]))
				#return
			else:	
				arrConditions.append(curItem)
		
			getLogger().info("Successfully processed Condition '{}'".format(cfgConditions[i]))
		return arrConditions
		
		
		
	def processOutputs(self, ruleName, cfgOutputs):
		arrOutputs = []
		# Outputs
		for i in range(len(cfgOutputs)):
			curItem = None
			#Complex node
			if hasConfigKey(cfgOutputs[i], KEY_TYPE):
				if getConfigValue(cfgOutputs[i], KEY_TYPE)== VALUE_ITEM:
				
					#TODO:: Might Need to read more values here?
					itemName = getConfigValue(cfgOutputs[i], KEY_NAME)
					
					#If timeout value is specified
					if hasConfigKey(cfgOutputs[i], KEY_TIMEOUT):
						delay = getConfigValue(cfgOutputs[i], KEY_DELAY, defaultValue=0, decode=False)
						timeout = getConfigValue(cfgOutputs[i], KEY_TIMEOUT)
						#TODO:: IMPLEMENT THIS!
						getLogger().warn("NOTICE: DimmerOutput not yet fully supported!")

						#TODO Check openHAB if it really is a dimmer
						if (hasConfigKey(cfgOutputs[i], KEY_ACTIVATED_VALUE) and hasConfigKey(cfgOutputs[i], KEY_DEACTIVATED_VALUE)):
							stateActivated = getConfigValue(cfgOutputs[i], KEY_ACTIVATED_VALUE, defaultValue=100, decode=False)
							stateDeactivated = getConfigValue(cfgOutputs[i], KEY_DEACTIVATED_VALUE, defaultValue=0, decode=False)
							getLogger().info("'SwitchOutput' -> itemName='{}', delay='{}', timeout='{}', stateActivated='{}', stateDeactivated='{}'".format(itemName, delay, timeout, stateActivated, stateDeactivated))
							curItem = DimmerOutput(itemName, stateActivated, stateDeactivated, delay, timeout)
						#At least a Timeout key should be specified
						else:
							getLogger().info("'SwitchOutput' -> itemName='{}', delay='{}', timeout='{}'".format(itemName, delay, timeout))
							curItem = SwitchOutput(itemName, delay, timeout)
					
					# just a plain switch item
					else:
						curItem = SwitchOutput(itemName, 0, 0)
			# Just the name of an openHAB item
			else:
				curItem = cfgOutputs[i]

			if curItem is None:
				getLogger().error("Invalid Output '{}'".format(arrOutputs[i]))
				#return
			else:	
				arrOutputs.append(curItem)
				
		return arrOutputs		


			
	def createTriggerRule(self, cfgRule):
		cfgTriggers = cfgRule[KEY_TRIGGERS]
		cfgConditions = cfgRule[KEY_CONDITIONS]
		cfgOutputs = cfgRule[KEY_OUTPUTS]
		ruleName = getConfigValue(cfgRule, KEY_NAME)

		arrTriggers = self.processTriggers(ruleName, cfgTriggers)
		arrConditions = self.processConditions(ruleName, cfgConditions)
		arrOutputs = self.processOutputs(ruleName, cfgOutputs)
		getLogger().debug("Loaded config for '{}' Triggers='{}', Conditions='{}', Outputs='{}'".format(ruleName, arrTriggers, arrConditions, arrOutputs))
		return StateTriggerRule(ruleName, arrTriggers, arrOutputs, arrConditions )
		#KEY_DELAY = 'delay'
		#KEY_TIMEOUT = 'timeout'
		
		#StateTriggerRule
		#return None
		#arr TimeInterval		
		##getRequiredConfigValue(KEY_DESCRIPTION)
		#return ScheduleRule(getRequiredConfigValue(KEY_NAME), 
		#			[TimeInterval("16:10", "16:50"), TimeInterval("17:00", "17:40"), TimeInterval("18:10", "18:50"), TimeInterval("19:10", "19:50"), TimeInterval("20:10", "20:50"), TimeInterval("21:10", "21:50"), TimeInterval("22:10", "22:50"), TimeInterval("23:10", "23:50"), TimeInterval("0:10", "0:50") ], 
		#			["switchLightLivingroomTest1"], 
		#			["switchLightScheduleTest", ActiveNightCondition()])


	def createScheduleRule(self, cfgRule):
		cfgSchedule = cfgRule[KEY_SCHEDULES]
		cfgConditions = cfgRule[KEY_CONDITIONS]
		cfgOutputs = cfgRule[KEY_OUTPUTS]
		
		ruleName = getConfigValue(cfgRule, KEY_NAME)
		
		arrSchedules = self.processSchedules(ruleName, cfgSchedule)
		arrConditions = self.processConditions(ruleName, cfgConditions)
		arrOutputs = self.processOutputs(ruleName, cfgOutputs)
		
		'''
		# Schedules
		for i in range(len(cfgSchedule)):
			#getLogger().info(("Time interval: '{}' - '{}'").format(cfgSchedule[i][KEY_BEGIN], cfgSchedule[i][KEY_END]))
			arrSchedules.append(TimeInterval(cfgSchedule[i][KEY_BEGIN], cfgSchedule[i][KEY_END]))

		
		# Conditions
		for i in range(len(cfgConditions)):
			curItem = None
			getLogger().info("Processing Condition '{}'".format(cfgConditions[i]))
			#Complex node
			if hasConfigKey(cfgConditions[i], KEY_TYPE):
				if getConfigValue(cfgConditions[i], KEY_TYPE)== VALUE_ITEM:
					#TODO:: Might need to read more values here?
					curItem = getConfigValue(cfgConditions[i], KEY_NAME)
					
				elif getConfigValue(cfgConditions[i], KEY_TYPE)== VALUE_CHECK:
					if getConfigValue(cfgConditions[i], KEY_NAME)==VALUE_ACTIVENIGHT:
						getLogger().info("Creating 'ActiveNight Condition")
						curItem = ActiveNightCondition()
			# Just the name of an openHAB item
			else:
				curItem = cfgConditions[i]
			
			getLogger().info("Condition is '{}'".format(curItem))
			if curItem is None:
				getLogger().error("Invalid configuration '{}'".format(cfgConditions[i]))
				#return
			else:	
				arrConditions.append(curItem)

			getLogger().info("Successfully processed Condition '{}'".format(cfgConditions[i]))
			
		
		# Outputs
		for i in range(len(cfgOutputs)):
			curItem = None
			#Complex node
			if hasConfigKey(cfgOutputs[i], KEY_TYPE):
				if getConfigValue(cfgOutputs[i], KEY_TYPE)== VALUE_ITEM:
					#TODO:: Might Need to read more values here?
					curItem = getConfigValue(cfgOutputs[i], KEY_NAME)
			# Just the name of an openHAB item
			else:
				curItem = cfgOutputs[i]

			if curItem is None:
				getLogger().error("Invalid Output '{}'".format(arrOutputs[i]))
				#return
			else:	
				arrOutputs.append(curItem)
		'''
		return ScheduleRule(ruleName, arrSchedules, arrOutputs, arrConditions )
		#getRequiredConfigValue(KEY_DESCRIPTION)
		#return ScheduleRule(getRequiredConfigValue(KEY_NAME), 
		#			[TimeInterval("16:10", "16:50"), TimeInterval("17:00", "17:40"), TimeInterval("18:10", "18:50"), TimeInterval("19:10", "19:50"), TimeInterval("20:10", "20:50"), TimeInterval("21:10", "21:50"), TimeInterval("22:10", "22:50"), TimeInterval("23:10", "23:50"), TimeInterval("0:10", "0:50") ], 
		#			["switchLightLivingroomTest1"], 
		#			["switchLightScheduleTest", ActiveNightCondition()])

		

		