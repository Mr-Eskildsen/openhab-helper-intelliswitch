from abc import ABCMeta, abstractmethod
from personal.intelliswitch.logging import LogException, getLogger

try:
	from core.jsr223.scope import OnOffType, OpenClosedType
	from personal.intelliswitch.base import BaseCore
	
except:
	LogException()


# ################################################
#
#	Base Outputs
#
# ################################################

class BaseOutput(BaseCore):
	__metaclass__ = ABCMeta	

	@abstractmethod
	def __init__(self, itemName, stateActivated, stateDeactivated, activateDelay, deactivateDelay):
		try:
			BaseCore.__init__(self, itemName)
			self._stateActivated = stateActivated
			self._stateDeactivated = stateDeactivated			
			self.delayActivate = activateDelay
			self.delayDeactivate = deactivateDelay
		except:
			LogException()
		
	def getActiveState(self):
		return self._stateActivated

	def getDeactiveState(self):
		return self._stateDeactivated
		
	def getActivateDelay(self):
		return self.delayActivate

	def getDeactivateDelay(self):
		return self.delayDeactivate


# ################################################
#
#	Binary Outputs
#
# ################################################

class SwitchOutput(BaseOutput):
	__metaclass__ = ABCMeta	

	def __init__(self, itemName, activateDelay, deactivateDelay):
		try:
			BaseOutput.__init__(self, itemName, OnOffType.ON, OnOffType.OFF, activateDelay, deactivateDelay)
		except:
			LogException()


class DimmerOutput(BaseOutput):
	__metaclass__ = ABCMeta	

	def __init__(self, itemName, stateActivated, stateDeactivated, activateDelay, deactivateDelay):
		try:
			BaseOutput.__init__(self, itemName, stateActivated, stateDeactivated, activateDelay, deactivateDelay)
		except:
			LogException()

