from abc import ABCMeta, abstractmethod
from core.jsr223.scope import itemRegistry
from core.osgi import get_service
from personal.intelliswitch.logging import LogException, getLogger

try:
	from personal.intelliswitch.device import OpenClosedDevice, OnOffDevice
except:
	LogException()


def getOpenHABItem(itemName):
 	return itemRegistry.getItem(itemName)


def getRuleManager():
	return get_service("org.openhab.core.automation.RuleManager") or get_service("org.eclipse.smarthome.automation.RuleManager") 
			
#def doesItemExistInOpenHAB(self, itemName):
#	try:
#	getLogger().warn("[IntelliSwitchManager] doesItemExistInOpenHAB: Seems to call wrong namespace!!!")
#	item_registry = osgi.get_service("org.eclipse.smarthome.core.items.ItemRegistry")
#	getLogger().debug("[IntelliSwitchManager]: 'doesItemExistInOpenHAB' Item to look for (Name='" + itemName + "')")
#	curItem = item_registry.getItem(str(itemName))
#	getLogger().debug("[IntelliSwitchManager]: 'doesItemExistInOpenHAB' Name of found Item (Item='" + curItem.name + "')")
#	
#	except: # catch *all* exceptions
#	LogException()
#	return False

		
def isItemOnOffType(itemName):
	return doesItemSupportOneOf(itemName, OnOffDevice.getAcceptedTypes())

	
def isItemOpenClosedType(itemName):
	return doesItemSupportOneOf(itemName, OpenClosedDevice.getAcceptedTypes())

	
def isItemBinaryType(itemName):
	return doesItemSupportOneOf(itemName, OnOffDevice.getAcceptedTypes() + OpenClosedDevice.getAcceptedTypes())

	
def doesItemSupportOneOf(itemName, types=[]):
	curItem = getOpenHABItem(itemName)
	if (len(list(set(curItem.getAcceptedDataTypes()) & set(types)))>0):
		return True
	return False


	