from core.osgi import get_service
from personal.intelliswitch.logging import LogException, getLogger

class Location(object):
	def __init__(self, lng, lat):
		self.longitude = lng
		self.latitude = lat
	
	def getLongitude(self):
		return self.longitude
		
	def getLatitude(self):
		return self.latitude

	@staticmethod
	def FromSystemLocation():
		LocationProvider = get_service("org.eclipse.smarthome.core.i18n.LocationProvider") 
		systemLocation = LocationProvider.getLocation()
		if (systemLocation is not None):
			return Location(systemLocation.getLongitude(), systemLocation.getLatitude())
		return None
