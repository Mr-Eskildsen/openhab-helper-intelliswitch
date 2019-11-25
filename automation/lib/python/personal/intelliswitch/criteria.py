from abc import ABCMeta, abstractmethod
from personal.intelliswitch.logging import getLogger, LogException
from personal.intelliswitch.utils import getClassName

#### Might need rework (because of smarthome)????
from org.eclipse.smarthome.core.library.types import DecimalType, OnOffType, OpenClosedType, PercentType, StringType

try:
	from personal.intelliswitch.base import BaseCore
	from personal.intelliswitch.oh import isItemBinaryType, isItemOnOffType, isItemOpenClosedType, getOpenHABItem
except:
	LogException()


class BaseCriteria(BaseCore):
	__metaclass__ = ABCMeta	
	
	@abstractmethod
	def __init__(self, name = ""):
		try:
			BaseCore.__init__(self, name)
		except:
			LogException()		
	
	@abstractmethod
	def isActive(self):
		pass
	
	@abstractmethod
	def getRequiredServices(self):
		return []

	def isOpenHABItem(self):
		return False
	
	def RequiresService(self, serviceId):
		return (serviceId in self.getRequiredServices())

	def EventHandler_ServiceDataUpdated(self, serviceId, data):
		getLogger().error(("Service data for '{}' was updated, but no handler was provided. Data is ignored").format(serviceId))
		
		
	def __repr__ (self):
		if (self.getName() is None) or (self.getName() == ""):
			return getClassName(self)
		return str(self.getName())

		
# ################################################
#
#	Binary Inputs
#
# ################################################
		
class BinaryCriteria(BaseCriteria):
	__metaclass__ = ABCMeta	

	@abstractmethod
	def __init__(self, itemName, activeState):
		try:
			BaseCriteria.__init__(self, itemName)
			self._item = getOpenHABItem(itemName)
			self._activeState = activeState
		except:
			LogException()

	def isOpenHABItem(self):
		return True
		
	def isActive(self):
		try:
			return (str(self._activeState)==str(self._item.getState()))
		except:
			LogException()
		return False

	@classmethod
	def CreateInstance(cls, itemName, activeState = None):
		if (isItemOnOffType(itemName)):
			if activeState is None:
				activeState = OnOffType.ON
			return OnOffCriteria(itemName, activeState)
			
		elif (isItemOpenClosedType(itemName)):
			if activeState is None:
				activeState = OpenClosedType.OPEN
			return OpenClosedCriteria(itemName, activeState)
		
		getLogger().error("BinaryCriteria could not be created for '%s', either a OnOff or a OpenClosed item is expected. The provided Item is none of those." % (itemName))
		return None
		
	def getRequiredServices(self):
		return BaseCriteria.getRequiredServices(self)
	
	
	
class OnOffCriteria(BinaryCriteria):
	__metaclass__ = ABCMeta	

	def __init__(self, itemName, activeState = OnOffType.ON):
		try:
			BinaryCriteria.__init__(self, itemName, str(activeState))
		except:
			LogException()

#	def isActive(self):
#		try:
#			return self._isStateActive()
#		except:
#			LogException()
#		return False

		
class OpenClosedCriteria(BinaryCriteria):
	__metaclass__ = ABCMeta	

	def __init__(self, itemName, activeState = OpenClosedType.OPEN):
		try:
			BinaryCriteria.__init__(self, itemName, str(activeState))
		except:
			LogException()
			
#	def isActive(self):
#		try:
#			return self._isStateActive( str(OpenClosedType.OPEN) )
#		except:
#			LogException()
#		return False
