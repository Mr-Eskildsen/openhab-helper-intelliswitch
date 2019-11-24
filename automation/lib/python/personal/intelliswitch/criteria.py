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
	def __init__(self, itemName):
		try:
			BaseCriteria.__init__(self, itemName)
			self._item = getOpenHABItem(itemName)
		except:
			LogException()

	def isOpenHABItem(self):
		return True
		
	def _isStateActive(self, activeStr):
		try:
			if (str(self._item.getState()) == activeStr):
				return True
		except:
			LogException()
		return False

	@classmethod
	def CreateInstance(cls, itemName):
		if (isItemOnOffType(itemName)):
			return OnOffCriteria(itemName)
		elif (isItemOpenClosedType(itemName)):
			return OpenClosedCriteria(itemName)
		
		getLogger().error("BinaryCriteria could not be created for '%s', either a OnOff or a OpenClosed item is expected. The provided Item is none of those." % (itemName))
		return None
		
	def getRequiredServices(self):
		return BaseCriteria.getRequiredServices(self)
	
	
	
class OnOffCriteria(BinaryCriteria):
	__metaclass__ = ABCMeta	

	def __init__(self, itemName):
		try:
			BinaryCriteria.__init__(self, itemName)
		except:
			LogException()

	def isActive(self):
		try:
			return self._isStateActive(str(OnOffType.ON))
		except:
			LogException()
		return False

		
class OpenClosedCriteria(BinaryCriteria):
	__metaclass__ = ABCMeta	

	def __init__(self, itemName):
		try:
			BinaryCriteria.__init__(self, itemName)
		except:
			LogException()
			
	def isActive(self):
		try:
			return self._isStateActive( str(OpenClosedType.OPEN) )
		except:
			LogException()
		return False