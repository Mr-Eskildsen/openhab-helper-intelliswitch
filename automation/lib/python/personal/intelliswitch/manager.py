from abc import ABCMeta, abstractmethod
import uuid
import traceback
from personal.intelliswitch.logging import LogException, getLogger

try:
	import core
	from core import osgi
	from core.jsr223 import scope, get_automation_manager
	from core.jsr223.scope import UnDefType, OnOffType, OpenClosedType, StringType, DecimalType
	from core.rules import addRule
	from core.triggers import EVERY_SECOND, EVERY_MINUTE, CronTrigger, ItemStateUpdateTrigger, ItemStateChangeTrigger, StartupTrigger
	
	from personal.intelliswitch.base import BaseCore
	
	from personal.intelliswitch.astro import getAstroSunInfo
	from personal.intelliswitch.condition import TimeInterval, ActiveNightCondition
	from personal.intelliswitch.device import DeviceFactory, PhysicalDevice, OnOffDevice, OpenClosedDevice, VirtualSwitch, VirtualTrigger
	from personal.intelliswitch.location import Location
	from personal.intelliswitch.output import DimmerOutput, SwitchOutput
	from personal.intelliswitch.rule import BaseRule, ScheduleRule, StateTriggerRule, MaintenanceRule
	from personal.intelliswitch.rulefactory import CronRuleFactory #, ScheduleRuleFactory, TriggerRuleFactory
	from personal.intelliswitch.service import RequiredServiceEnum
	from personal.intelliswitch.utils import getDateToday, ParseTimeStringToDate
	
	from personal.intelliswitch.utils import getClassName
	from personal.intelliswitch.rule import BaseRule

except:
	LogException()

scope.scriptExtension.importPreset("RuleSimple")
scope.scriptExtension.importPreset("RuleSupport")

#TODO:: To be removed
#Removed 2019-11-22
#CRONTRIGGER_ID = "CronTrigger"

#TODO:: To be removed
#Removed 2019-11-23
#STARTUP_MODULE_ID = "MyModule"


#TODO:: Merge into Intelliswitch class
class RuleManagerCore(BaseCore):

	@abstractmethod
	def __init__(self, _name, _description):
		
		try:
			#Initialize empty dictionary for physical devices
			self.dictPhysicalDevices = {}
			self.dictVirtualSwitches = {}
			self._dictRuleProxies = {} 
			self.arrConditionalItems = []
			self.description = _description
			BaseCore.__init__(self, _name)
			
			
			# Create Housekeeping Cron Job
			#ruleCronMaintain = CronRuleFactory("IntelliSwitch - {} (Maintenance)".format(_name), _description, self)
			#ruleCronMaintain.AddCronTrigger(EVERY_MINUTE)
			#self._ruleCronMaintain = ruleCronMaintain
			
			# TODO:: Fix Startup Rule - Considder if it is really needed
			self._ruleCronMaintain = None
			self._ruleStartup = None 

			#StartupRuleFactory(_name, _description, self)
			#self._dictRuleProxies = {} 
		except:
			LogException()

			
	def getDescription(self):
		return self.description
		
		
	def RegisterConditionalItem(self, itemName):
		try:
			if (itemName not in self.arrConditionalItems):
				self.arrConditionalItems.append(itemName)
			
			# HEST
			#if (ruleProxy.getId() not in self._dictRuleProxies):
			#	self._dictRuleProxies[ruleProxy.getId()] = ruleProxy
			#return ruleProxy.getId()
		except:
			LogException()
		return None

		
	def RegisterProxyRule(self, ruleProxy):
		try:
			if (ruleProxy.getId() not in self._dictRuleProxies):
				self._dictRuleProxies[ruleProxy.getId()] = ruleProxy
			return ruleProxy.getId()
		except:
			LogException()
		return None
		
	def Commit(self):
		try:
		
			# Create and register Maintenance rule
			self._ruleCronMaintain = MaintenanceRule("[Maintenance]", self.getDescription(), self.arrConditionalItems)
			self.Add(self._ruleCronMaintain)
			
			#ruleMaintain
			#HEST
			#self.RegisterProxyRule(
			
			'''
			# Make sure Maintenance rule is started and also run
			if (self._ruleCronMaintain is not None):
				# Add conditional triggers to rule
				#for curItemName in self.arrConditionalItems:
				#	getLogger().info(("Adding openHAB item '{}' as conditional trigger").format(curItemName))
				#	self._ruleCronMaintain.AddItemStateChangeTrigger(curItemName)
					
				if (self._ruleCronMaintain.hasTriggers()):
					
					newRule = addRule(self._ruleCronMaintain)
					getLogger().info(("Activated '{}' rule (uid='{}')").format(self._ruleCronMaintain.getConfigName(), newRule))
					self._ruleCronMaintain.setRuleUID(newRule.UID)
					# Run Rule now
					self._ruleCronMaintain.runNow()
			'''							
			#if (self._ruleCronMaintain is not None):
			#	getLogger().warn("'StartupTrigger' is programatically disabled")
			#
			#	#if (self._ruleCronMaintain.hasTriggers()):
			#	#	scope.automationManager.addRule(self._ruleCronMaintain)
			#	#	getLogger().info("Activated 'StartupTrigger' rule")
				
			for key, ruleProxy in self._dictRuleProxies.items():
					if (ruleProxy.hasTriggers()):
						newRule = addRule(ruleProxy)
						ruleProxy.setRuleUID(newRule.UID)
						getLogger().info(("Added '{}' rule (uid='{}')").format(ruleProxy.getConfigName(), newRule.UID))
					else:
						getLogger().warn(("Rule '{}' was not added, because no triggers was specified for rule").format(ruleProxy.getConfigName()))
			
			#Manual run Maintenance rule to initialize properly
			self._ruleCronMaintain.runNow()
			
		except:
			LogException()	
	


	def subscribeItemStateUpdateEvent(self, ruleUID, itemName):
		try:
			triggerName = itemName
			getLogger().info("Adding ItemStateUpdateTrigger for item '{}', triggerName='{}', ruleUID='{}'".format(itemName, triggerName, ruleUID))
			self._subscribeTriggerEvent(ruleUID, itemName, ItemStateUpdateTrigger(itemName, None, triggerName))
		except:
			LogException()

	def subscribeItemStateChangedEvent(self, ruleUID, itemName):
		try:
			triggerName = itemName
			getLogger().info("Adding ItemStateChangeTrigger for item '{}', triggerName='{}', ruleUID='{}'".format(itemName, triggerName, ruleUID))
			self._subscribeTriggerEvent(ruleUID, itemName, ItemStateChangeTrigger(itemName, None, None, triggerName))
		except:
			LogException()
			


	def subscribeItemCommandEvent(self, ruleUID, itemName):
		try:
			triggerName = itemName
			getLogger().info("Adding ItemCommandTrigger for item '{}', triggerName='{}', ruleUID='{}'".format(itemName, triggerName, ruleUID))
			
			self._subscribeTriggerEvent(ruleUID, itemName, ItemCommandTrigger(itemName, None, triggerName))
		except:
			LogException()
			

	'''	
	#Removed 2019-11-22
	def AddCronTrigger(self, cronExpression = EVERY_MINUTE):
		try:
			getLogger().info("Adding CronTrigger '" + CRONTRIGGER_ID + "'")
			self._subscribeTriggerEvent(self._ruleCronjob.getId() ,CRONTRIGGER_ID, CronTrigger(cronExpression, CRONTRIGGER_ID))
		except:
			LogException()

	
	def AddStartupTrigger(self, startupTriggerId = "StartupTrigger"):
		try:
			getLogger().info("Adding StartupTrigger '" + startupTriggerId + "'")
			#TODO:: Eventually send None as Name, this will force it to use a guuid instead
			startupTrigger = StartupTrigger(startupTriggerId)
			self._subscribeTriggerEvent(_ruleCronMaintain.getId(), startupTriggerId, startupTrigger)
		except:
			LogException()
	'''


	def _subscribeTriggerEvent(self, ruleId, triggerName, trigger):
		try:
			getLogger().debug("'_subscribeTriggerEvent': ruleId='{}' triggerName='{}".format(ruleId, triggerName))
			# TODO:: Validate if item has a Physical Switch if it is a item related switch
			
			#register callback for item related switches (to PhysicalDevice)
			'''
			if (isinstance(trigger, CronTrigger)):
				triggerHandler = self._ruleCronMaintain

			el
			'''
			if (isinstance(trigger, StartupTrigger)):
				triggerHandler = self._ruleStartup
			else:
				if self._dictRuleProxies.has_key(ruleId):
					triggerHandler = self._dictRuleProxies[ruleId]
				
			if (triggerHandler is not None):
				getLogger().info("'subscribeTriggerEvent' - Adding '{}'".format(triggerName))
				triggerHandler._AddTriggerCore(trigger)
			else:
				getLogger().info("Failed to subscribe trigger event for '{}' (ruleId='{}')".format(triggerName, ruleId))
			

		except:
			LogException()
			
	
	# ######################################################################
	#
	#	Method:	createPhysicalDevice
	# ######################################################################
	def createPhysicalDevice(self, deviceName):
		try:
			# 1. Check that items exist in openHAB
			# ######################################################################
				
		
			# 2. Check if it already exists in the dictionary, else create
			# ######################################################################
			if (self.dictPhysicalDevices.has_key(deviceName)==False):

				getLogger().info("Creating new PhysicalDevice '" + deviceName + "'")
				device = DeviceFactory.Create(deviceName)
				
				if (device is None):
					getLogger().error(("New PhysicalDevice '{}' could not be created!!!!").format(deviceName))
					return None
					
				self.dictPhysicalDevices[deviceName] = device
								
				getLogger().debug("New PhysicalDevice added to dictionary: '" + str(self.dictPhysicalDevices) + "'")
				getLogger().debug("Added new PhysicalDevice '" + deviceName + "' to triggers")
				

		except:
			LogException()
			return None
			
		# 3. return PhysicalDevice
		# ######################################################################
		return self.dictPhysicalDevices[deviceName]

		
	def getPhysicalDevice(self, deviceName):
		if (self.dictPhysicalDevices.has_key(deviceName)==False):
			getLogger().warn("PhysicalDevice not found for '" + deviceName + "'")
			getLogger().debug(("PhysicalDevice dictionary -> {}").format(self.dictPhysicalDevices))
			return None

		return self.dictPhysicalDevices[deviceName]


	# ######################################################################
	#
	#	Method:	createVirtualSwitch
	# ######################################################################
	def createVirtualSwitch(self, virtualItemName, physicalDeviceName, strSwitchPurpose = ""):
		return self.createVirtualSwitchAdvanced(virtualItemName, physicalDeviceName, OnOffTYpe.ON, OnOffType.OFF, 0, 0, strSwitchPurpose)
	

	def createVirtualSwitchAdvanced(self, virtualItemName, physicalDeviceName, activeState, inactiveState, activateDelay, deactivateDelay, strSwitchPurpose = ""):
		curVirtualSwitch = None
		try:
			getLogger().debug("Create VirtualSwitch '" + str(physicalDeviceName) + "' for virtualItem='" + virtualItemName +"'")
			
			# 1. Get/Create Physical Switch
			# ######################################################################
			physicalDevice = self.createPhysicalDevice(physicalDeviceName)
			if (physicalDevice == None):
				getLogger().error(("Unable to create PhysicalDevice for '{}'.").format(physicalDeviceName))
				return None
			
			# 1. Create VirutalSwitch
			# ######################################################################
			uniqueName = RuleManager.GenerateVirtualItemUniqueName(virtualItemName, physicalDevice.getName(), strSwitchPurpose)
			curVirtualSwitch = VirtualSwitch(uniqueName, physicalDevice, activateDelay, deactivateDelay)
			if (self.dictVirtualSwitches.has_key(curVirtualSwitch.getId())):
				getLogger().error("VirtualSwitch with name '" + uniqueName + "' already exist")
			else:
				self.dictVirtualSwitches[curVirtualSwitch.getId()] = curVirtualSwitch
				getLogger().info("Added new VirtualSwitch '" + curVirtualSwitch.getName() + "' to dictionary")
				getLogger().debug("New VirtualSwicth dictionary: '" + str(self.dictVirtualSwitches) + "'")
		except:
			LogException()
		return curVirtualSwitch

	def createVirtualOutputAdvanced(self, virtualItemName, physicalDeviceName, actualItem, strSwitchPurpose = ""):
		curVirtualSwitch = None
		try:
			getLogger().debug("Create VirtualSwitch '" + str(physicalDeviceName) + "' for virtualItem='" + virtualItemName +"'")
			
			# 1. Get/Create Physical Switch
			# ######################################################################
			physicalDevice = self.createPhysicalDevice(physicalDeviceName)
			if (physicalDevice == None):
				getLogger().error(("Unable to create PhysicalDevice for '{}'.").format(physicalDeviceName))
				return None
				
			# 1. Create VirutalSwitch
			# ######################################################################
			uniqueName = RuleManager.GenerateVirtualItemUniqueName(virtualItemName, physicalDevice.getName(), strSwitchPurpose)
								
			if (isinstance(actualItem, SwitchOutput)):
				curVirtualSwitch = VirtualSwitch(uniqueName, physicalDevice, actualItem.getActivateDelay(), actualItem.getDeactivateDelay())
				
			elif (isinstance(actualItem, DimmerOutput)):
				curVirtualSwitch = VirtualDimmer(uniqueName, physicalDevice, actualItem.getActiveState(), actualItem.getDeactiveState(), actualItem.getActivateDelay(), actualItem.getDeactivateDelay())

			else:
				curVirtualSwitch = VirtualSwitch(uniqueName, physicalDevice, actualItem.getActivateDelay(), actualItem.getDeactivateDelay())


			if (self.dictVirtualSwitches.has_key(curVirtualSwitch.getId())):
				getLogger().error("VirtualSwitch with name '" + uniqueName + "' already exist")
			else:
				self.dictVirtualSwitches[curVirtualSwitch.getId()] = curVirtualSwitch
				getLogger().info("Added new VirtualSwitch '" + curVirtualSwitch.getName() + "' to dictionary")
				getLogger().debug("New VirtualSwicth dictionary: '" + str(self.dictVirtualSwitches) + "'")
		except:
			LogException()
		return curVirtualSwitch
		
		
	# ######################################################################
	#
	#	Method:	createVirtualTrigger
	# ######################################################################
	def createVirtualTrigger(self, virtualItemName, physicalDeviceName, ruleId, eventHandler):
		curVirtualTrigger = None
		try:
			getLogger().debug("Register Trigger for PhysicalDevice '{}' in configuration '{}' (ruleId='{}'".format(physicalDeviceName, virtualItemName, ruleId))
		
			# 1. Get/Create Physical Switch
			# ######################################################################
			physicalDevice = self.createPhysicalDevice(physicalDeviceName)
			self.subscribeItemStateChangedEvent(ruleId, physicalDeviceName)
			
			# 2. Create VirtualTrigger
			# ######################################################################
			virtualItemUniqueName = RuleManager.GenerateVirtualItemUniqueName(virtualItemName, physicalDevice.getName())
			curVirtualTrigger = VirtualTrigger( virtualItemUniqueName, physicalDevice, eventHandler )
			physicalDevice.subscribeEvents( virtualItemName, curVirtualTrigger.EventHandler_TriggerStateChanged)
			getLogger().info("Added new VirtualTrigger '{}' to dictionary".format(virtualItemUniqueName))
		except:			
			LogException()
			return None

		return curVirtualTrigger
				
	# ######################################################################
	#
	#	Method:	subscribeEventStateChanged
	# ######################################################################
	def subscribeEventStateChanged(self, ruleId, physicalDeviceName, eventHandler):
		try:
			getLogger().debug("Subscripe EventStateChanged  for PhysicalDevice '" + physicalDeviceName + "'")
		
			# 1. Get/Create Physical Switch
			# ######################################################################
			physicalDevice = self.createPhysicalDevice(physicalDeviceName)
			self.subscribeItemStateChangedEvent(ruleId, physicalDeviceName)
			
			# 2. Subscribe Event
			# ######################################################################
			virtualItemUniqueName = RuleManager.GenerateVirtualItemUniqueName(virtualItemName, physicalDevice.getName())
			physicalDevice.subscribeEvents( str(uuid.uuid4()), eventHandler)
			
		except:			
			LogException()

			
	@staticmethod
	def GenerateVirtualItemUniqueName(virtualItemName, physicalItemName, postFix = ""):

		#if (len(postFix)>0):
		#	return physicalItemName + "_" + virtualItemName + "_" + postFix
		#	
		#return physicalItemName + "_" + virtualItemName
		return physicalItemName + "_" + str(uuid.uuid4())

		
		
	#
	#	EventHandler for Item State Changed Triggers
	#
	#
	# ###########################################################################
	def EventHandler_ItemStateChanged(self, ruleId, itemName, oldState, newState, eventString):
		getLogger().info("ItemStateChanged from '{}' to '{}' for '{}' (eventString='{}')".format(oldState, newState, itemName, eventString))
		physicalDevice = self.getPhysicalDevice(itemName)
		if (physicalDevice is None):
			getLogger().error("No PhysicalDevice found for item='{}' cannot process event".format(itemName))
		else:
			getLogger().debug("Sending 'ItemStateChanged' event to physical device '{}'".format(itemName))
			physicalDevice.StateChangedEvent(oldState, newState, eventString)

	#
	#	EventHandler for Item State Updated Triggers
	#
	#
	# ###########################################################################
	def EventHandler_ItemStateUpdated(self, ruleId, itemName, state, eventString):
		getLogger().info("ItemStateChanged from '{}' to '{}' for '{}' (eventString='{}')".format(oldState, newState, itemName, eventString))
		physicalDevice = self.getPhysicalDevice(itemName)
		if (physicalDevice is None):
			getLogger().error("No PhysicalDevice found for item='{}' cannot process event".format(itemName))
		else:
			getLogger().debug("Sending 'ItemStateUpdated' event to '" + itemName + "'")
			physicalDevice.StateUpdatedEvent(state, eventString)
		
	#
	#	EventHandler for CronJob
	# ###########################################################################@abstractmethod
	@abstractmethod
	def EventHandler_CronJob(self, ruleId):
		pass

	#
	#	EventHandler for StartupJob
	# ###########################################################################
	'''
	@abstractmethod
	def EventHandler_StartupJob(self, ruleId):
		pass
	'''

#def str2bool(v):
#  return str(v).lower() in ("yes", "true", "t", "1")




class RuleManager(RuleManagerCore):
	__metaclass__ = ABCMeta
	
	def __init__(self, _name, _description, location = None):
		try:
			RuleManagerCore.__init__(self, _name, _description)

			self._location = location
			self.astroUseCount = 0
			self.astroLastUpdated = getDateToday().minusDays(1)
			self._astroSunInfo = None
			
			self.dictRules = {}
	
			#2019.11.22 TODO::  CRON TRIGGER Removed
			#self.AddCronTrigger(EVERY_MINUTE)
			
			#2019.11.17 TODO:: Fix Trigger
			#self.AddStartupTrigger(STARTUP_TRIGGER_ID)
							
		except:
			LogException()
			return	
		
	
	# ######################################################################
	#
	#	Method:	Add
	#	
	#
	# ######################################################################
	def Add(self, newRule):

		try:
			if (isinstance(newRule, BaseRule)==False):
				#getLogger().error(u"Configuration '{}' is instance of '{}', it should be instance of class that inherits from 'BaseConfig'".format(newRule.getName().decode('utf8'), getClassName(newRule)))
				getLogger().error("Configuration '{}' is instance of '{}', it should be instance of class that inherits from 'BaseConfig'".format(newRule.getName(), getClassName(newRule)))
				return False

			getLogger().debug(("Adding Rule Type='{}',  ConfigName='{}', OutputItems='{}'").format(newRule.__class__.__name__, newRule.getName(), str(newRule.getOutputItems())))
						
			# Initialize rule 
			newRule.InitializeConfig(self)
			
			if (newRule.RequiresService(RequiredServiceEnum.ASTRO)):
				getLogger().debug("Rule '{}' requires 'Astro' service".format(newRule.getName()))
				self.astroUseCount = self.astroUseCount + 1
				
			getLogger().debug(("Adding Rule '{}' to dictionary (Id='{}')").format(newRule.getName(), newRule.getId()))
			self.dictRules[newRule.getId()] = newRule
			if (self.dictRules.has_key(newRule.getId())):
				getLogger().debug("Rule '{}' was added successfully (Id='{}')".format(newRule.getName(), newRule.getId()))
			else:
				getLogger().error("Rule '{}' was not added to dictionary (Id='{}')".format(newRule.getName(), newRule.getId()))
		except:
			LogException()
			return False	
	

	@staticmethod
	def GenerateVirtualSwitchKey(configName, physicalItemName, postFix = ""):
		if (len(postFix)>0):
			return ("{}_{}_{}").format(physicalItemName, configName, postFix)
		return ("{}_{}").format(physicalItemName, configName)

		
	def EventHandler_CronJob(self, ruleId, ruleUID):
		try:
			#getLogger().debug("Processing EventHandler_CronJob for RuleManager ruleId='{}', ruleUID='{}'".format(ruleId, ruleUID))
			
			#Check if the triggering rule UID is maintenance rule 
			'''
			if ((self._ruleCronMaintain is not None) and (self._ruleCronMaintain.getRuleUID()==ruleUID)):
				self.onCronJobMaintain()
				
			el
			'''
			if (self.dictRules.has_key(ruleId)):
				curRule = self.dictRules[ruleId]
				curRule.EventHandler_CronJob()
				
			else:
				getLogger().error("Rule not found when processing EventHandler_CronJob (RuleUID='{}')".format(ruleUID))
		except:
			LogException()
			return False
		return True
		

	def onCronJobMaintain(self):
		try:
			astroIsUpdated = False
			getLogger().debug("Processing Maintenance Cron Job for RuleManager....")

			# Recalc SunInfo if needed
			if ((self.astroUseCount > 0) and (self.astroLastUpdated.isBefore(getDateToday()))):
				getLogger().info(("Astro data outdated (lastUpdate='{}')").format(self.astroLastUpdated))
				updateDate = getDateToday()

				self.sunInfoYesterday = getAstroSunInfo(updateDate.minusDays(1), self._location.getLatitude(), self._location.getLongitude())
				self.sunInfoToday = getAstroSunInfo(updateDate, self._location.getLatitude(), self._location.getLongitude())
				self.sunInfoTomorrow = getAstroSunInfo(updateDate.plusDays(1), self._location.getLatitude(), self._location.getLongitude())
				if (self.sunInfoYesterday is None or self.sunInfoToday is None or self.sunInfoTomorrow is None):
					getLogger().warn(("CronJob failed to get updated sunrise and sunset data from Astro (lastUpdate='{}')").format(self.astroLastUpdated))
					return False
				else:
					self._astroSunInfo = [self.sunInfoYesterday, self.sunInfoToday, self.sunInfoTomorrow ]
					astroIsUpdated = True
					self.astroLastUpdated = updateDate
					getLogger().debug(("CronJob updated sunrise and sunset for lat='{}' long='{}' from Astro action (lastUpdate='{}')").format(self._location.getLatitude(), self._location.getLongitude(), self.astroLastUpdated))
					getLogger().debug(("Astro SunInfo Yesterday: '{}' - '{}'").format(self._astroSunInfo[0].getSunriseStart(), self._astroSunInfo[0].getSunriseEnd(), self._astroSunInfo[0].getSunsetStart(), self._astroSunInfo[0].getSunsetEnd()))
					getLogger().debug(("Astro SunInfo Today    : '{}' - '{}'").format(self._astroSunInfo[1].getSunriseStart(), self._astroSunInfo[1].getSunriseEnd(), self._astroSunInfo[1].getSunsetStart(), self._astroSunInfo[1].getSunsetEnd()))
					getLogger().debug(("Astro SunInfo Tomorrow : '{}' - '{}'").format(self._astroSunInfo[2].getSunriseStart(), self._astroSunInfo[2].getSunriseEnd(), self._astroSunInfo[2].getSunsetStart(), self._astroSunInfo[2].getSunsetEnd()))

			for key, curRule in self.dictRules.iteritems():
				getLogger().debug(("Performing Maintenance job for rule '{}' (Id='{}', Key='{}')").format(curRule.getName(), curRule.getId(), key))
				
				if(astroIsUpdated): 
					curRule.EventHandler_ServiceDataUpdated(RequiredServiceEnum.ASTRO, self._astroSunInfo)


				curProxyRuleState = curRule.getProxyRuleState()
				curConditionState = curRule.GetConditionActiveStatus()
					
				getLogger().debug(("Checking status for '{}'. RuleStatus:'{}' ConditionStatus:'{}'").format(curRule.getName(), curProxyRuleState, curConditionState))
				if (curProxyRuleState != curConditionState):
					getLogger().info("openHAB rule '{}' has Enabled Status='{}', required state is '{}'".format(curRule.getName(), curProxyRuleState, curConditionState))
					
					curRule.UpdateState()
					
					##If rule is deactivated
					#if (curProxyRuleState):
					#	curRule.UpdateState()
					
					# make sure openHAB rule is (de)activated according to needs
					curRule.setProxyRuleState(curConditionState)
					
					##If rule is activated
					#if (curConditionState):
					#	curRule.UpdateState()
				
				
		except:
			LogException()
			return False
		return True
	'''	
	def EventHandler_StartupJob(self, ruleId):
		try:
			for curConfigName, curConfig in self.dictRules.iteritems():
				curConfig.EventHandler_StartupJob(ruleId)
		except:
			LogException()
			return False
		return True
	'''	

