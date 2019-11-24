from abc import ABCMeta, abstractmethod
import uuid
from personal.intelliswitch.logging import getLogger, LogException

try:
	
	from org.joda.time import DateTime
	#from core.osgi import get_service
	from core.jsr223.scope import UnDefType, OnOffType, OpenClosedType, StringType, DecimalType
	from core.triggers import EVERY_SECOND, EVERY_MINUTE, CronTrigger, ItemStateUpdateTrigger, ItemStateChangeTrigger, StartupTrigger

	import core
	from core.jsr223 import scope, get_automation_manager
	
	
	from personal.intelliswitch.oh import getRuleManager
except:
	LogException()

scope.scriptExtension.importPreset("RuleSimple")
scope.scriptExtension.importPreset("RuleSupport")



CRONTRIGGER_ID = "CronTrigger"
STARTUPTRIGGER_ID = "StartupTrigger"

	

class RuleFactory(scope.SimpleRule): 
	
	@abstractmethod
	def __init__(self, configName, _name, _description, manager):
		try:
			self._id = str(uuid.uuid4())
			self._ruleUID = None
			self._ruleObj = None
			self.name = _name
			self.description = _description
			self._manager = manager

			getLogger().debug("Creating new rule '{}'".format(configName))
			self.triggers = []
			self._configName = configName
		except:
			LogException()
	
	
			
	def getRuleUID(self):
		return self._ruleUID

	def setRuleUID(self, ruleUID):
		self._ruleUID = ruleUID
		
	def getId(self):
		return self._id
	
		
	def getConfigName(self):
		return self._configName
	
	def hasTriggers(self):
		if (len(self.triggers)>0):
			return True
		return False
	
	def setRule(self, rule):
		self._ruleObj = rule
	
	def _AddTriggerCore(self, newTrigger, triggerName = None, description = None):
		if (triggerName is not None):
			newTrigger.name = triggerName
			#newTrigger.description = "##TODO - Proper description##"
		self.triggers.append(newTrigger.trigger)
		
	def AddItemStateUpdateTrigger(self, itemName):
		try:
			triggerName = itemName
			getLogger().info("Adding ItemStateUpdateTrigger for item='{}', trigger='{}'".format(itemName, triggerName))
			newTrigger = ItemStateUpdateTrigger(itemName, triggerName=triggerName)
			self._AddTriggerCore(newTrigger, triggerName)
		except:
			LogException()
			
	def AddItemStateChangeTrigger(self, itemName):
		try:
			triggerName = itemName
			getLogger().info("Adding ItemStateChangeTrigger for item='{}', trigger='{}'".format(itemName, triggerName))
			self._AddTriggerCore(ItemStateChangeTrigger(itemName, triggerName=triggerName), triggerName)
		except:
			LogException()

	def AddItemCommandTrigger(self, itemName):
		try:
			triggerName = itemName
			getLogger().info("Adding ItemCommandTrigger for item='{}', trigger='{}'".format(itemName, triggerName))
			self._AddTriggerCore(ItemCommandTrigger(itemName, triggerName=triggerName), triggerName)
		except:
			LogException()
		
	def AddItemEventTrigger(self, eventSource, eventType, eventTopic, triggerName):
		try:
			getLogger().info("Adding ItemEventTrigger for eventSource '" + eventSource + "'")
			self._AddTriggerCore(ItemEventTrigger(eventSource, eventType, eventTopic, triggerName), triggerName)
		except:
			LogException()

	def AddStartupTrigger(self, triggerName = STARTUPTRIGGER_ID):
		try:
			getLogger().info("Adding StartupTrigger '" + triggerName + "'")
			self._AddTriggerCore(StartupTrigger(triggerName))
		except:
			LogException()

	def AddCronTrigger(self, cronExpression = EVERY_MINUTE, triggerName = ""):
		try:
			getLogger().info("Adding CronTrigger '{}' with schedule='{}'".format(triggerName, cronExpression))
			self._AddTriggerCore(CronTrigger(cronExpression, triggerName), triggerName)
		except:
			LogException()

	def setEnabled(self, newState):
		try:
			if ((self._ruleUID is not None) and (getRuleManager() is not None)):	
				getRuleManager().setEnabled(self._ruleUID, newState)
				getLogger().info("Enabled state of rule '{}', was changed to '{}'".format(self._ruleUID, newState))
			else:
				getLogger().error("Not able to alter enabled state of rule '{}'".format(self._ruleUID))
		except:
			LogException()
			
			
	def isEnabled(self):
		try:
			if ((self._ruleUID is not None) and (getRuleManager() is not None)):
				return getRuleManager().isEnabled(self._ruleUID)
			else:
				getLogger().error("Not able to query enabled state of rule '{}'".format(self._ruleUID))
		except:
			LogException()

		return False
		
		
	def runNow(self):
		try:
			if ((self._ruleUID is not None) and (getRuleManager() is not None)):
				getLogger().debug(("Manual execute rule '{}' UID='{}'").format(self.getConfigName(), self._ruleUID))
				getRuleManager().runNow(self._ruleUID)
		except:
			LogException()

			
	def execute(self, module, inputs):
		try:
			ruleId = None 
			itemName = ""

			if (self._ruleObj is not None):
				ruleId = self._ruleObj.getId()
				
			getLogger().debug("Calling EventHandler for '{}' (module='{}' inputs='{}' ruleId='{}')".format(self.getConfigName(), module, inputs, ruleId))
			
			if (inputs.has_key('event')):
				event = inputs['event']
				getLogger().debug(("EVENT: '{}'").format(event))
				getLogger().debug(("ITEMNAME: '{}'").format(inputs['event'].getItemName()))
				itemName = inputs['event'].getItemName()
				
			if ((self.getConfigName() == CRONTRIGGER_ID) or (self.getConfigName() == STARTUPTRIGGER_ID)):
				getLogger().debug("'" + self.getConfigName() + "': Trigger activated (module='" + str(module) + "', input='" + str(inputs) + "'")
			else:
				getLogger().debug("'" + self.getConfigName() + "': Trigger activated (module='" + str(module) + "', input='" + str(inputs) + "'")
			
			# ItemStateUpdated Event occurred
			if (inputs.has_key('module') & inputs.has_key('event') & inputs.has_key('state')):
				#Call EventHandler in Manager (to allow update of shared variables)
				self._manager.EventHandler_ItemStateUpdated(ruleId, itemName, str(inputs['state']), str(inputs['event']))
				return True
				
			# ItemStateChanged Event occurred
			elif (inputs.has_key('module') & inputs.has_key('event') & inputs.has_key('oldState') & inputs.has_key('newState')):
				#Call EventHandler in Manager (to allow update of shared variables)
				self._manager.EventHandler_ItemStateChanged(ruleId, itemName, str(inputs['oldState']), str(inputs['newState']), str(inputs['event']))
				return True

			# It is either a StartupTrigger or a CronTrigger. Both has no parameters
			else:
				self._manager.EventHandler_CronJob(ruleId, self.getRuleUID())
				return True
				'''
				if (self.getConfigName() == CRONTRIGGER_ID):
					#Call EventHandler in Manager (to allow update of shared variables)
					self._manager.EventHandler_CronJob(ruleId)
					return True
				elif (self.getConfigName() == STARTUPTRIGGER_ID):
					#Call EventHandler in Manager (to allow update of shared variables)
					self._manager.EventHandler_StartupJob(ruleId)
					return True
				'''
			getLogger().error("Could not identify proper EventHandler for '{}' (module='{}' inputs='{}')".format(self.getConfigName(), module, inputs))
					
		except:
			LogException()
			return False
		return True


		

class CronRuleFactory(RuleFactory): 
	__metaclass__ = ABCMeta
	
	def __init__(self, _name, _description, manager):
		try:
			RuleFactory.__init__(self, CRONTRIGGER_ID, _name, _description, manager)
		except:
			LogException()

			
class StartupRuleFactory(RuleFactory): 
	__metaclass__ = ABCMeta
	
	def __init__(self, _name, _description, manager):
		try:
			RuleFactory.__init__(self, STARTUPTRIGGER_ID, _name, _description, manager)
		except:
			LogException()

class TriggerRuleFactory(RuleFactory): 
	__metaclass__ = ABCMeta
	
	def __init__(self, configName, _name, _description, manager):
		try:
			RuleFactory.__init__(self, configName, _name, _description, manager)
		except:
			LogException()

