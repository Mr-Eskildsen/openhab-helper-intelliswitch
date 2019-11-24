import threading
from abc import ABCMeta, abstractmethod

from personal.intelliswitch.logging import LogException, getLogger

try:
	from core.jsr223 import scope
	from core.jsr223.scope import events, itemRegistry, UnDefType, OnOffType, OpenClosedType, StringType, DecimalType
	from personal.intelliswitch.base import BaseCore 
	from personal.intelliswitch.event import ItemStateChangedEvent, ItemStateUpdatedEvent
	from personal.intelliswitch.utils import getClassName
except:
	LogException()


class DeviceFactory(BaseCore):
	@classmethod
	def Create(cls, itemName):
		try:
			curItem = scope.itemRegistry.getItem(itemName)
			
			getLogger().debug(("DeviceFactory: Item accepts datatypes: '{}'").format(curItem.getAcceptedDataTypes()))

			#
			# BinaryDevice
			# #############################################
			
			#Check if we should create a OnOffDevice
			if (len(list(set(curItem.getAcceptedDataTypes()) & set(OnOffDevice.getAcceptedTypes())))>0):
				return OnOffDevice(itemName)

			#Check if we should create a OpenClosedDevice
			elif (len(list(set(curItem.getAcceptedDataTypes()) & set(OpenClosedDevice.getAcceptedTypes())))>0):
				return OpenClosedDevice(itemName)

			#Check if we should create a NumberDevice
			elif (len(list(set(curItem.getAcceptedDataTypes()) & set(NumberDevice.getAcceptedTypes())))>0):
				return NumberDevice(itemName, moduleName)
			
			#Check if we should create a StringDevice
			elif (len(list(set(curItem.getAcceptedDataTypes()) & set(StringDevice.getAcceptedTypes())))>0):
				return StringDevice(itemName)
			
			else:
				getLogger().error(("ItemType for '{}' not supported in DeviceFactory.Create()").format(itemName))
				
		except:
			LogException()
		
		return None
		

# #########################################################
#	Class: PhysicalDevice (abstract)
#
#
# ########################################################


class PhysicalDevice(BaseCore):
	__metaclass__ = ABCMeta	
		
	@classmethod
	def getAcceptedTypes(cls):
		return []
		
	@abstractmethod
	def __init__(self, name):
		try:
			self._state = None
			self.usageCount = 0
			self.callbacks = {}

			#Create Synchronization object
			self.lock = threading.Lock()

			BaseCore.__init__(self, name)

		except:
			LogException()
	
	
	def subscribeEvents(self, subscriberId, callback):
		try:
			getLogger().debug("Added subscription for events (Item='" + self.getName() +"', Subscriber='" + subscriberId + "')")
			self.callbacks[subscriberId] = callback
		except:
			LogException()
			
	#
	# Push event to all virtualDevices that subscribes for events
	def fireEvent(self, event):
		try:
			getLogger().debug("fireEvent called for '" + self.getName() + "' event='" + str(event) + "'")
			for key, value in self.callbacks.iteritems():
				getLogger().debug("Calling callback for subscriber='" + str(key) + "'")
				value(event)
		except:
			LogException()
	
	#Return True if event is handled
	def onProcessEvent(self, event):
		return False
		
	def fireStateChangedEvent(self, oldState, newState, eventStr):
		try:
			#getLogger().debug("fireStateChangedEvent called for '" + self.getName() + "' oldState='" + oldState + "', newState='" + newState + "', event='" + eventStr + "'")
			getLogger().debug(("fireStateChangedEvent called for '{}' oldState='{}', newState='{}', event='{}'").format(self.getName(), oldState, newState, eventStr))
			# TODO:: Check if this could/should  be something else
			curEvent = ItemStateChangedEvent(self.getName())
			curEvent.source = self
			curEvent.itemName = str(self.getName())
			curEvent.oldState = str(oldState)
			curEvent.newState = str(newState)
			curEvent.event = str(eventStr)
	
			if (self.onProcessEvent(curEvent) == False):
				self.fireEvent(curEvent)

		except:
			LogException()
			return False
		return True
		
	def fireStateUpdatedEvent(self, state, eventStr):
		try:
			getLogger().debug(("StateUpdatedEvent called for '{}' state='{}', event='{}'").format(self.getName(), state, eventStr))
			e = ItemStateUpdatedEvent(self.getName())
			e.source = self
			e.itemName = str(self.getName())
			e.state = str(state)
			e.event = str(eventStr)
			
			self.fireEvent(e)

		except:
			LogException()
			return False
		return True

	def StateChangedEvent(self, oldState, newState, eventStr):
		try:
			getLogger().debug("StateChangedEvent called for '" + self.getName() + "' oldState='" + oldState + "', newState='" + newState + "', event='" + eventStr + "'")
			self._state = newState
			self.fireStateChangedEvent(oldState, newState, eventStr)
		except:
			LogException()
			return False		
		return True
		
		
	def StateUpdatedEvent(self, state, eventStr):
		try:
			getLogger().debug("StateUpdatedEvent called for '" + self.getName() + "' state='" + state + "', event='" + eventStr + "'")
			self._state = state
			self.fireStateUpdatedEvent(state, eventStr)
		except:
			LogException()
			return False
		return True
		

		
# #########################################################
#	Class: BinaryDevice (abstract)
#
#
# ########################################################
class BinaryDevice(PhysicalDevice):
	__metaclass__ = ABCMeta	
	
	@abstractmethod
	def __init__(self, name):
		try:
			
			PhysicalDevice.__init__(self, name)
			
			curItem = scope.itemRegistry.getItem(self.getName())
			strState = str(curItem.state).upper()
			getLogger().debug(("Initialize BinaryDevice '{}', current state is '{}' (Type='{}')").format(self.getName(), curItem.state, type(curItem.state)))
			if (strState == 'NULL'):
				getLogger().info(("BinaryDevice '{}' is in uninitialized state. Changing state from '{}' to state '{}'").format(self.getName(), curItem.state, self.getStateInactive()))
				events.sendCommand(curItem, self.getStateInactive())
		except:
			LogException()

	@abstractmethod		
	def getStateActive(self):
		pass
		
	@abstractmethod		
	def getStateInactive(self):
		pass

	def forceState(self, requiredState):
		getLogger().debug(("Calling 'BinaryDevice::forceState' for '{}'   requiredState='{}' actualState='{}'").format(self.getName(), str(requiredState), str(curItem.state).upper()))
		
		
	#	curItem = itemRegistry.getItem(self.getName())
	#	if (str(curItem.state).upper()!=requiredState):
	#		events.sendCommand(curItem, requiredState)
		
	def incrementUsageCount(self):
		try:
			getLogger().debug("Calling 'incrementUsageCount' for '" + self.getName() + "'  count='" + str(self.usageCount) + "'")
			with self.lock:
				self.usageCount = self.usageCount + 1
				getLogger().debug("Increment usage count for '" + self.getName() + "' to '" + str(self.usageCount) + "'")
				if (self.usageCount > 0):
					getLogger().info(("'sendCommand' called for item '{}' newState='{}'").format(self.getName(), self.getStateActive()))
					curItem = itemRegistry.getItem(self.getName())
					events.sendCommand(curItem, self.getStateActive())
		except:
			LogException()
		
	def decrementUsageCount(self):
		try:
			getLogger().debug("calling 'decrementUsageCount' for '" + self.getName() + "'  count='" + str(self.usageCount) + "'")
			with self.lock:
				if (self.usageCount>0):
					self.usageCount = self.usageCount - 1
					getLogger().debug("Decrement usage count for '" + self.getName() + "' to '" +str(self.usageCount)+ "'")
					if (self.usageCount<1):
						getLogger().info("'sendCommand' called for item '" + self.getName() + "' newState='"+ str(self.getStateInactive()) + "'")
						curItem = itemRegistry.getItem(self.getName())
						events.sendCommand(curItem, self.getStateInactive())

							
		except:
			LogException()
		
			
			
# #########################################################
#	Class: OnOffDevice 
#		Wrapper for Items that accepts On/Off as states
#
# ########################################################
class OnOffDevice(BinaryDevice):
	__metaclass__ = ABCMeta	

	@classmethod
	def getAcceptedTypes(cls):
		return [OnOffType]

	def __init__(self, name):
		try:
			BinaryDevice.__init__(self, name)

		except:
			LogException()
	
	
	def getStateActive(self):
		return OnOffType.ON

	
	def getStateInactive(self):
		return OnOffType.OFF

		
# #########################################################
#	Class: OpenClosedDevice 
#		Wrapper for Items that accepts Open/Closed as states
#
# ########################################################
class OpenClosedDevice(BinaryDevice):
	__metaclass__ = ABCMeta	

	@classmethod
	def getAcceptedTypes(cls):
		return [OpenClosedType]

	def __init__(self, name):
		try:
			BinaryDevice.__init__(self, name)

		except:
			LogException()
			
	@classmethod
	def getStateActive(cls):
		return OpenClosedType.OPEN
		
	@classmethod
	def getStateInactive(cls):
		return OpenClosedType.CLOSED

			
			
class GenericDevice(PhysicalDevice):
	__metaclass__ = ABCMeta	
	
	@abstractmethod
	def __init__(self, name):
		try:
			PhysicalDevice.__init__(self, name)

		except:
			LogException()

		
					
class StringDevice(GenericDevice):
	__metaclass__ = ABCMeta	
	
	@classmethod
	def getAcceptedTypes(cls):
		return [StringType]
		
	def __init__(self, name):
		try:
			GenericDevice.__init__(self, name)
		except:
			LogException()

					
class NumberDevice(GenericDevice):
	__metaclass__ = ABCMeta	
	
	@classmethod
	def getAcceptedTypes(cls):
		return [DecimalType]
	
	def __init__(self, name):
		try:
			GenericDevice.__init__(self, name)
		except:
			LogException()
		
			
			
		
# #########################################################
#	Class: VirtualItem (abstract)
#		Base class for the Virtual wrappers
#
# ########################################################
class VirtualItem(BaseCore):
	__metaclass__ = ABCMeta	

	@abstractmethod
	def __init__(self, name, physicalDevice, eventCallback):
		try:
			
			BaseCore.__init__(self, name)
			
			#Initialization
			self._activated = False
			self._physicalDevice = None
			self._eventCallback = eventCallback
			#Validation
			if (physicalDevice is not None):
				if (isinstance(physicalDevice, PhysicalDevice)==False):
					getLogger().error("Instance of PhysicalDevice not instance of class 'PhysicalDevice'. Actual instance is '" + getClassName(physicalDevice) + "'")
					#TODO:: Raise Exception
				
				self._physicalDevice = physicalDevice
		except:
			LogException()
	
	def onEvent(self, event):
		pass
		
	def EventHandler_TriggerStateChanged(self, event):
		try:
		
			self.onEvent(event)
			if (self._eventCallback is not None):
				self._eventCallback(event)
		except:
			LogException()
		
	
	@abstractmethod
	def updateState(self, newValue):		
		pass
		
	def isActive(self):
		return self._activated
	
	def forceState(self, state):
		if (self._physicalDevice != None):
			self._physicalDevice.forceState(state)

# #########################################################
#	Class: VirtualSwitch
#		Virtual class that can interact with a BinaryDevice
#
# ########################################################
class VirtualOutputItem(VirtualItem):
	__metaclass__ = ABCMeta	

	def __init__(self, name, physicalDevice, activeState, inactiveState, activateDelay, deactivateDelay):
		try:
			self._delayActivateTimer = None
			self._delayDeactivateTimer = None
			self._activeState = activeState
			self._inactiveState = inactiveState 
			self.delayActivate = float(activateDelay)
			self.delayDeactivate = float(deactivateDelay)
			VirtualItem.__init__(self, name, physicalDevice, None)
			getLogger().info(("Create VirtualSwitch '{}' - states='{}'/'{}', delayActivate='{}', delayDeactivate='{}', type='{}' ").format(name, self._activeState, self._inactiveState, self.delayActivate, self.delayDeactivate, self.__class__.__name__))
		except:
			LogException()
			
	def updateState(self, newValue):
		try:
			getLogger().debug(("Calling 'updateState' with newValue='{}' for '{}' (ActivateDelay='{}', DeactivateDelay='{}')").format(newValue, self.getName(), self.delayActivate, self.delayDeactivate))
			if (newValue==True):
				if self.delayActivate==0:
					self.incrementUsage()
				else:
					getLogger().debug(("Calling Calling Timer to activate Delay='{}'").format(self.delayActivate))
					if (self._delayActivateTimer is not None):
						self._delayActivateTimer.cancel()
					self._delayActivateTimer = threading.Timer(self.delayActivate, self.incrementUsage)
					self._delayActivateTimer.start()
					
			else:
				if self.delayDeactivate==0:
					self.decrementUsage()
				else:
					getLogger().debug(("Calling Calling Timer to deactivate Delay='{}'").format(self.delayDeactivate))
					if (self._delayDeactivateTimer is not None):
						self._delayDeactivateTimer.cancel()
						
					self._delayDeactivateTimer = threading.Timer(self.delayDeactivate, self.decrementUsage)
					self._delayDeactivateTimer.start()
		except:
			LogException()

	def getInactiveState(self):
		return self._inactiveState

	def getActiveState(self):
		return self._activeState

			
	def incrementUsage(self):
		if (self._delayActivateTimer is not None):
			self._delayActivateTimer = None
			
		if (self._activated==False):
			self._physicalDevice.incrementUsageCount()#self.getActiveState())
			self._activated = True

			
	def decrementUsage(self):			
		if (self._delayDeactivateTimer is not None):
			self._delayDeactivateTimer = None
			
		if (self._activated==True):
			self._physicalDevice.decrementUsageCount() #self.getInactiveState())
			self._activated = False				




# #########################################################
#	Class: VirtualSwitch
#		Virtual class that can interact with a BinaryDevice
#
# ########################################################
class VirtualSwitch(VirtualOutputItem):
	__metaclass__ = ABCMeta	

	def __init__(self, name, physicalDevice, activateDelay, deactivateDelay):
		try:
			VirtualOutputItem.__init__(self, name, physicalDevice, OnOffType.ON, OnOffType.OFF, activateDelay, deactivateDelay)
			#getLogger().info(("Create VirtualSwitch '{}' - delayActivate='{}', delayDeactivate='{}'").format(name, self.delayActivate, self.delayDeactivate))
		except:
			LogException()
	


# #########################################################
#	Class: VirtualDimmer
#		Virtual class that can interact with a BinaryDevice
#
# ########################################################
class VirtualDimmer(VirtualOutputItem):
	__metaclass__ = ABCMeta	

	def __init__(self, name, moduleName, physicalDevice, activeState, inactiveState, activateDelay, deactivateDelay):
		try:
			VirtualOutputItem.__init__(self, name, moduleName, physicalDevice, activeState, inactiveState, activateDelay, deactivateDelay)
			#getLogger().info(("Create VirtualDimmer '{}' - states='{}'/'{}', delayActivate='{}', delayDeactivate='{}'").format(name, activeState, inactiveState, self.delayActivate, self.delayDeactivate))
		except:
			LogException()
			



# #########################################################
#	Class: VirtualTrigger
#		Virtual class that can handle incomming events only 
#
# ########################################################
class VirtualTrigger(VirtualItem):
	__metaclass__ = ABCMeta	
	
	def __init__(self, name, physicalDevice, eventCallback):
		try:
			getLogger().debug("Creating instance of VirtualTrigger name='" + name + "'")
			VirtualItem.__init__(self, name, physicalDevice, eventCallback)
		except:
			LogException()
		
	def onEvent(self, event):
		try:
			getLogger().debug("Calling 'onEvent' for VirtualTrigger name='" + self.getName() + "'")
			newActiveState = False
			#TODO:: Make this generic
			if event.getState() in ('ON', 'OPEN'):
				newActiveState = True
			
			self.updateState(newActiveState)
		except:
			LogException()
		
		
		
	def updateState(self, newValue):
		try:
			getLogger().debug("Calling 'updateState' with newValue='" + str(newValue) + "' for '" + self.getName() + "'")
			self._activated = newValue
		except:
			LogException()
	
	