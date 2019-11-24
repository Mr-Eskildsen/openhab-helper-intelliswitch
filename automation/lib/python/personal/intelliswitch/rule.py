from abc import ABCMeta, abstractmethod

from personal.intelliswitch.logging import LogException, LogDeprecated, getLogger

try:
	from core.triggers import EVERY_MINUTE
	from core.jsr223.scope import events, itemRegistry, OnOffType, OpenClosedType
	from personal.intelliswitch.base import BaseCore
	import personal.intelliswitch.service as Core_Service
	from personal.intelliswitch.output import SwitchOutput, DimmerOutput
	from personal.intelliswitch.condition import ConditionManager, TimeScheduleCondition, TimeInterval, SequenceCondition
	from personal.intelliswitch.rulefactory import CronRuleFactory, TriggerRuleFactory
except:
	LogException()

def generateRuleName(managerName, ruleName):
	return ("IntelliSwitch - {}: {}").format(managerName, ruleName)
		
# ##########################################################################
#
#	Class: BaseRule
#
# ##########################################################################	
class BaseRule(BaseCore):
	__metaclass__ = ABCMeta	
	

	@abstractmethod
	def __init__(self, name, description, arrTriggerItems, arrOutputItems, arrConditions):
		try:
			self.requestedTriggeredState = False
			self.actualTriggeredState = False

			BaseCore.__init__(self, name)
			self._description = description
			self._configValid = True
			self._mgr = None
			self._proxyHandler = None
			self._conditionMgr = ConditionManager()

			self._arrRequiredService = []
			self._arrVirtualTriggers = {}
			self._arrVirtualSwitches = {}
			
			self._arrOutputItems = arrOutputItems
			self._arrTriggerItems = arrTriggerItems
			self._conditionMgr.Add( arrConditions )

			getLogger().debug(("Created new rule '{}' - Triggers='{}', Outputs='{}', Conditions='{}'").format(name, self._arrTriggerItems, self._arrOutputItems, arrConditions))
		except:		
			LogException()
		
		
	def getDescription(self):	
		return self._description
	
	
	
	def getManager(self):
		return self._mgr
	
	def AddRequiredService(self, input):
		try:
			self._arrRequiredService = list(set(self._arrRequiredService + input.getRequiredServices()))
		except:
			LogException()
			

	def RequiresService(self, serviceId):
		return (serviceId in self._arrRequiredService)

	
	def setProxyHandler(self, proxy):
		self._proxyHandler = proxy
		
	def getProxyHandler(self):
		return self._proxyHandler
		
	def getProxyRuleState(self):
		return self.getProxyHandler().isEnabled()
		
	def setProxyRuleState(self, newState):
		if self.getProxyHandler():
			self.getProxyHandler().setEnabled(newState)

	def runNow(self):
		try:
			ruleUID = None
			if (self._proxyHandler is not None):
				ruleUID = self._proxyHandler.getRuleUID()

			getLogger().debug("calling 'runNow' for '{}' (ruleUID='{}')".format(self.getName(), ruleUID))
			self.getProxyHandler().runNow()
		except:
			LogException()
			return				
			
	#
	# Initialzies the rule
	#
	def InitializeConfig(self, manager):
		try:
			self._mgr = manager

			getLogger().info("'Initialize Config' for '" + self.getName() + "'")

			# TODO:: Fix Description
			# Register Rule in manager
			if (isinstance(self, ScheduleRule) or isinstance(self, MaintenanceRule)):
				newRuleProxy = CronRuleFactory(generateRuleName(self._mgr.getName(), self.getName()), self.getDescription(), self._mgr)	
				newRuleProxy.AddCronTrigger(EVERY_MINUTE, "Cron: Every Minute")
			elif (isinstance(self, StateTriggerRule)):
				newRuleProxy = TriggerRuleFactory(self.getName(), generateRuleName(self._mgr.getName() ,self.getName()), self.getDescription(), self._mgr)	
			else:
				getLogger().error(("Failed to create rule '{}'. Class '{}' not supported").format(self.getName(), getClassName(self)))
				return False

			ruleId = self._mgr.RegisterProxyRule(newRuleProxy)
			# Set Proxy Handler in Rule
			self.setProxyHandler(newRuleProxy)
			# Set Rule in Proxy Handler
			newRuleProxy.setRule(self)
			
			
			# Process all output switches
			# ######################################################################
			for idx in range(len(self._arrOutputItems)):
				actualItem = self._arrOutputItems[idx]			
				delayActivate = 0
				delayDeactivate = 0
				stateActive = OnOffType.ON
				stateInactive = OnOffType.OFF
			
				if (isinstance(actualItem, basestring)):
					curItemName = actualItem
					itemOutput = SwitchOutput(actualItem, 0, 0)
				else:
					itemOutput = actualItem
								
				#elif (isinstance(actualItem, SwitchOutput)):
				#	curItemName = actualItem.getName()
				#	delayActivate = actualItem.getActivateDelay()
				#	delayDeactivate = actualItem.getDeactivateDelay()
				
				#elif (isinstance(actualItem, RangeOutput)):
				#	curItemName = actualItem.getName()
				#	delayActivate = actualItem.getActivateDelay()
				#	delayDeactivate = actualItem.getDeactivateDelay()
				#	stateActive = actualItem.getActiveState()
				#	stateInactive = actualItem.getDeactiveState()
				
				# 1. Fail if item it doesn't exist in openHAB
				# ######################################################################
				getLogger().debug(("Processing switch '{}' - stateActive='{}', stateInactive='{}', delayActivate='{}', delayDeactivate='{}'").format(itemOutput.getName(), itemOutput.getActiveState(), itemOutput.getDeactiveState(), itemOutput.getActivateDelay(), itemOutput.getDeactivateDelay()))

				
				# 2. Make sure both PhysicalDevice and VirtualSwitch is created and 
				#		add to Dictionary (Fail if exist)
				# ######################################################################

				curVirtualSwitch = manager.createVirtualOutputAdvanced(self.getName(), itemOutput.getName(), itemOutput)
				
				self._arrVirtualSwitches[itemOutput.getName()] = curVirtualSwitch
				getLogger().info(("Created VirtualSwitch '{}'").format(curVirtualSwitch.getName(), itemOutput.getName() ))
				getLogger().debug(("VirtualSwitch dictionary now has entries: '{}'").format(self._arrVirtualSwitches))

			
			getLogger().debug("Creating Trigger swicthes")
				
			# Create PhysicalDevices for all Triggers and add to Dictionary
			# Register a callback in the PhysicalDevice, to handle Triggers
			# ######################################################################
			for curTriggerItem in self._arrTriggerItems:

				#TODO:: Here we should handle to ability to use Input classes as triggers,a s well as Item Names of Binary Items
				curPhysicalDevice = None
				getLogger().debug("Processing Trigger '" + curTriggerItem + "'")
				

				# Register Callback in PhysicalDevice for Triggers
				# ######################################################################
				curVirtualTrigger = self.getManager().createVirtualTrigger(self.getName(), curTriggerItem, ruleId, self.EventHandler_TriggerStateChanged)				
				self._arrVirtualTriggers[curTriggerItem] = curVirtualTrigger

			
			#Adding all required services and conditional triggers from conditions 
			for curCondition in self._conditionMgr.conditions:
				self.AddRequiredService(curCondition)
				if curCondition.isOpenHABItem():
					self._mgr.RegisterConditionalItem(curCondition.getName())
					getLogger().debug("CONDITION: '{}' is openHAB item".format(curCondition))
				else:
					getLogger().debug("CONDITION: '{}' is NOT openHAB item".format(curCondition))
				
			getLogger().info(("'{}' required services '{}' has been added").format(self.getName(), self._arrRequiredService))
			# TODO:: 
			#	#Considderations
			#	# A. Considder if the PhysicalDevice might need a trigger to the openHAB item (to catch changes form elsewhere (inside openHAB))
			
			
		except:
			LogException()
			return False	
		return True
		
		
	
	def getOutputItems(self):
		return self._arrOutputItems
	
	def getSwitchItems(self):
		LogDeprecated("Method is deprecated. Use 'getOutputItems' instead")
		return self._arrOutputItems
	
	def getVirtualSwitchByName(self, name):
		return self._arrVirtualSwitches[name]
	
	def EventHandler_ServiceDataUpdated(self, serviceId, data):
		try:
			for curCondition in self._conditionMgr.conditions:
				if (curCondition.RequiresService(serviceId)):
					curCondition.EventHandler_ServiceDataUpdated(serviceId, data)
		except:	
			LogException()
			
	'''		
	def EventHandler_StartupJob(self, ruleId):
		getLogger().warn("No handler implemented for 'EventHandler_StartupJob'")
		return True
	'''
	
	def GetConditionActiveStatus(self):
		return self._conditionMgr.isActive()
	
	def GetRequestedTriggerState(self):
		return self.requestedTriggeredState
	
	def SetRequestedTriggerState(self, newState):
		self.requestedTriggeredState = newState
	
	def EventHandler_CronJob(self):
		try:
			ruleUID = None
			if (self._proxyHandler is not None):
				ruleUID = self._proxyHandler.getRuleUID()

			getLogger().debug(("Processing EventHandler_CronJob for '{}' (RuleUID='{}')").format(self.getName(), ruleUID))
			self.UpdateState()
			self.onCronJob()
		except:		
			LogException()

	def onCronJob(self):
		pass
		
	def EventHandler_TriggerStateChanged(self, event):
		try:
			ruleUID = None
			if (self._proxyHandler is not None):
				ruleUID = self._proxyHandler.getRuleUID()

			getLogger().debug("EventHandler_TriggerStateChanged called for '{}' because item '{}' was changed or updated to state '{}' (Event='{}' RuleUID='{}')".format(self.getName(), event.itemName, str(event.getState()), event.event, ruleUID))
			self.EvaluateTrigger(event)
		except:
			LogException()
			return				

	def EvaluateTrigger(self, event):
		try:
			ruleUID = None
			if (self._proxyHandler is not None):
				ruleUID = self._proxyHandler.getRuleUID()

			getLogger().debug("EvaluateTrigger called for rule '{}' because item '{}' was changed or updated to state '{}' (Event='{}' RuleUID='{}')".format(self.getName(), event.itemName, str(event.getState()), event.event, ruleUID))

			newActiveState = False
			for curTriggerName, curTrigger in self._arrVirtualTriggers.iteritems():
				newActiveState = newActiveState or curTrigger.isActive()
			
			if (self.GetRequestedTriggerState() != newActiveState):
				self.SetRequestedTriggerState(newActiveState)

			#Do the update (which checks both Trigger and Conditions)
			self.UpdateState()

		except:
			LogException()
			return			

			
	def UpdateState(self):
		try:
			curConditionState = self.GetConditionActiveStatus()
			curRequestedState = self.GetRequestedTriggerState()
			curAllowedState = curConditionState & curRequestedState
			actualTriggerState = self.actualTriggeredState
			
			getLogger().debug(("Calling 'UpdateState' for '{}': curConditionState='{}', requestedTriggeredState='{}', actualAllowedState='{}', actualTriggerState='{}'").format(self.getName(), curConditionState, str(curRequestedState), str(curAllowedState), str(actualTriggerState)))
			if (curAllowedState != actualTriggerState):
				
				#Loop  over virtual switches instead
				getLogger().debug(("Processing all VirtualSwitches: '{}'").format(self._arrVirtualSwitches))
				
				for itemName, curItem in self._arrVirtualSwitches.items():
					getLogger().debug(("Update state for '{}'....").format(self.getName()))	
					curItem.updateState(curAllowedState)
				
				getLogger().info(("Rule '{}' has changed state from '{}' to '{}'").format( self.getName(), actualTriggerState, curRequestedState))
				self.actualTriggeredState = curAllowedState
				
			# TODO:: ThIS Might solve problem with items not being cut off?
			
			#getLogger().debug(("'{}' Processing all VirtualSwitches: '{}'").format(self.getName(), self._arrVirtualSwitches))
			
			#for itemName, curItem in self._arrVirtualSwitches.items():
			#	getLogger().debug(("'{}' Processing VirtualSwitch: '{}'").format(self.getName(), itemName))
			#	if (curAllowedState != actualTriggerState):
			#		getLogger().debug(("Update state for '{}'....").format(self.getName()))	
			#		curItem.updateState(curAllowedState)
			
			#getLogger().info(("Rule '{}' has changed state from '{}' to '{}'").format( self.getName(), actualTriggerState, curRequestedState))
			#self.actualTriggeredState = curAllowedState
			
		except:
			LogException()
				
	@abstractmethod
	def toStringProperties(self):
		pass

		
	def __repr__ (self):
		return "[" + self.__class__.__name__ + " name='" + str(self.getName()) + "' outputs='" + str(self._arrOutputItems) + "' conditions='" + str(self._conditionMgr.conditions) + "', triggers='" + str(self._arrTriggerItems) +  "', " + self.toStringProperties() + "]"

		
# ##########################################################################
#
#	Class: StateTriggerRule
#	Status:	Working
#
# ##########################################################################	
class StateTriggerRule(BaseRule):
	__metaclass__ = ABCMeta	

	def __init__(self, name, arrTriggerItems, arrOutputItems, arrConditions = [], description = ''):
		try:
			BaseRule.__init__(self, name, description, arrTriggerItems, arrOutputItems, arrConditions)
			getLogger().debug("Created configuration '" + str(name) + "' with " + str(len(arrTriggerItems)) + " triggers and "+ str(len(arrConditions))  + " conditions")
		except:
			LogException()
			return				

	
	
	def toStringProperties(self):
		pass
	
	
# ##########################################################################
#
#	Class: TriggerRule
#	Status:	Not implemented

#	Trigger High/Low (NormallyClosed or NormallyOpen)
#
#
# ##########################################################################	
'''
class TriggerRule(BaseRule):
	__metaclass__ = ABCMeta	

	def __init__(self, name, arrTriggerItems, arrOutputItems, arrConditions = []):
		try:
		
			BaseRule.__init__(self, name, arrTriggerItems, arrOutputItems, arrConditions)
			
			getLogger().debug("Created configuration '" + str(name) + "' with " + str(len(arrTriggerItems)) + " triggers and "+ str(len(arrConditions))  + " conditions")
			
		except:
			LogException()
			return				

	
	
	def toStringProperties(self):
		pass
'''		
# ##########################################################################
#
#	Class: ScheduleRule
#	Status:	Prerelease
#
# ##########################################################################	
class ScheduleRule(BaseRule):
	__metaclass__ = ABCMeta	

	def __init__(self, name, arrTimeSchedule, arrOutputItems, arrConditions = [], description = ''):
		
		try:
			getLogger().debug(("Initialize 'ScheduleRule': Name='{}, TimeSchedule='{}', OutputItems='{}', Conditions='{}'").format(name, arrTimeSchedule, arrOutputItems, arrConditions))
			
			#Validate TimeIntervals
			for idx in range(len(arrTimeSchedule)):
				if (isinstance(arrTimeSchedule[idx], TimeInterval)==False):
					getLogger().error("'" + name + "' has invalid TimeInterval at index " + str(idx) + ", a valid parameter must be of type 'TimeInterval'")
					self._configValid = False
			
			#First add conditions (assume they are easiest to evaluate)
			conditions = arrConditions
			conditions.append( TimeScheduleCondition(arrTimeSchedule) )
			
			#No TriggerItems!
			BaseRule.__init__(self, name, description, [], arrOutputItems, conditions)
			
		except:
			LogException()
			return				

	def EventHandler_TriggerStateChanged(self, event):
		 message = "EventHandler_TriggerStateChanged not supported for 'ScheduleRule'"
		 getLogger().error(message)
		 raise NotImplementedError(message)

	# This is just a hack to ensure that the Physical Switch follows the virtual switch
	def onCronJob(self):
		getLogger().debug(("'onCronJob' called for '{}'....").format(self.getName()))	
		try:
			curConditionState = self.GetConditionActiveStatus()
			curRequestedState = self.GetRequestedTriggerState()
			curAllowedState = curConditionState & curRequestedState
		
			getLogger().debug(("'onCronJob' called for '{}'....").format(self.getName()))	
			if (curConditionState):
				for itemName, curItem in self._arrVirtualSwitches.items():
					getLogger().debug(("'onCronJob' processing item '{}' ('{}')....").format(itemName, curItem))	
					physicalItem = itemRegistry.getItem(itemName)
					#events.sendCommand(curItem, self.getStateInactive())getLogger().debug(("Calling 'forceState for '{}' requestedState='{}' curState='{}' conditionState='{}'....").format(itemName, curRequestedState, str(curItem.state).upper(), curConditionState))
					newState = curItem._physicalDevice.getStateInactive()
					if (curRequestedState):
						newState = curItem._physicalDevice.getStateActive()
					
					if (newState != physicalItem.state):
						events.sendCommand(physicalItem, newState)
					
			else:
				getLogger().debug("'onCronJob' skipping (ConditionState is FALSE)")	
		except:
			LogException()
			return				

		
	# Overide default behaviour, since this is a non-trigegred class
	def GetRequestedTriggerState(self):
		return True
		
	def toStringProperties(self):
		return "" #schedules='" + str(self._arrTimeSchedule) + "'"
	
"""	
# ##########################################################################
#
#	Class: SequenceRule
#	Status:	Not Implemented
#
# ##########################################################################	
class SequenceRule(BaseRule):
	__metaclass__ = ABCMeta	
	
	
	def __init__(self, name, cycleDuratation, arrSequenceItems, arrConditions = [], description = ''):
	
		try:
			getLogger().info(("Initialize SequenceRule '{}' (CycleDuration='{}', SequenceItems='{}', conditions='{}'").format(name, cycleDuratation, arrSequenceItems, arrConditions))
			self._cycleDuration = cycleDuratation
			self._cycleOverlap = 0

			#Create list of names for Switch items so that base class handles creation of switches
			arrOutputItems = []
			for curSequenceItem in arrSequenceItems:
				getLogger().info(("SequenceRule - processing SequenceItem: '{}' ").format(curSequenceItem))
			
				#Only add item once
				if (curSequenceItem.getName() not in arrOutputItems):
					getLogger().info(("SequenceRule - Adding SequenceItem: '{}' ").format(curSequenceItem))
					arrOutputItems.append(curSequenceItem.getName())
				
			#First add other conditions (assume they are easiest to evaluate)
			conditions = arrConditions
			conditions.append(SequenceCondition(self, self._cycleDuration, arrSequenceItems) )				

			#No TriggerItems
			BaseRule.__init__(self, name, description, [], arrOutputItems, conditions)
			
		except:
			LogException()
			return				

	
	def EventHandler_TriggerStateChanged(self, event):
		 message = "EventHandler_TriggerStateChanged not supported for 'SequenceRule'"
		 getLogger().error(message)
		 raise NotImplementedError(message)
			
	# Overide default behaviour, since this is a non-triggered class
	def GetRequestedTriggerState(self):
		return True
		
	def toStringProperties(self):
		return ""

"""	
		
# ##########################################################################
#
#	Class	: MaintenanceRule
#	Purpose : Ensures Housekeepping is done
#	Status	: Prerelease
#
# ##########################################################################	
class MaintenanceRule(BaseRule):
	__metaclass__ = ABCMeta	
	
	def __init__(self, name, description, arrTriggerItems):
		
		try:
			getLogger().debug(("Initialize 'MaintenanceRule': Name='{}").format(name))
			
			#No Condition or Output items!
			BaseRule.__init__(self, name, description, arrTriggerItems, [], [])
			
		except:
			LogException()
			return				
			
	def EventHandler_CronJob(self):
		try:
			self.getManager().onCronJobMaintain()
		except:		
			LogException()

	def onCronJob(self):
		pass
		
	def EventHandler_TriggerStateChanged(self, event):
		try:
			#TODO:: Find a better way than calling the full Cron Job
			self.getManager().onCronJobMaintain()
		except:
			LogException()
			return				

	# Overide default behaviour, since this is a non-triggered class
	def GetRequestedTriggerState(self):
		return True
		
	def toStringProperties(self):
		return "" #schedules='" + str(self._arrTimeSchedule) + "'"

		