from abc import ABCMeta, abstractmethod
from personal.intelliswitch.logging import LogException, getLogger

try:
	from personal.intelliswitch.base import BaseCore
	from personal.intelliswitch.utils import getClassName
except:
	LogException()





class EventCore(BaseCore):

	@abstractmethod
	
	def __init__(self):
		BaseCore.__init__(self, "")
		self.event = ""
		
		
class ItemEventCore(EventCore):

	
	def __init__(self, _itemName):
		EventCore.__init__(self)
		
		self.itemName = _itemName
		self.state = ""
		

	def getState(self):
		return self.state

	def __repr__ (self):
		return "[" + self.__class__.__name__ + " itemName='" + str(self.itemName) + "' state='" + str(self.state) + "' event='" + str(self.event) + "']"

		
class ItemStateUpdatedEvent(ItemEventCore):
	
	def __init__(self, _itemName):
		ItemEventCore.__init__(self, _itemName)

class ItemStateChangedEvent(ItemEventCore):
	
	def __init__(self, _itemName):
		try:
			ItemEventCore.__init__(self, _itemName) #, moduleName)
			self.oldState = ""
			self.newState = ""
		except:
			LogException()


	def getState(self):
		return self.newState

	def getPrevState(self):
		return self.oldState
		
	def __repr__ (self):
		return "[" + self.__class__.__name__ + " itemName='" + str(self.itemName) + "' state='" + str(self.getState()) + "' oldState='" + str(self.oldState) + "' newState='" + str(self.newState) + "' event='" + str(self.event) + "']"
		

class CronEvent(EventCore):
	def __init__(self):
		try:
			EventCore.__init__(self)
		except:
			LogException()
		
