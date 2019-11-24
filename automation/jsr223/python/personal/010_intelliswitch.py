import traceback
import core


from core.osgi import get_service 
from core.jsr223 import scope, get_automation_manager
from core.log import LOG_PREFIX

from personal.intelliswitch.logging import getLogger, LogException

logger = getLogger("{}.personal.intelliswitch".format(LOG_PREFIX))

try:
	from personal.intelliswitch.config import IntelliSwitchManager
except:
	LogException()

configuration = None


# Check for a valid configuration
try:
	from configuration import intelliswitch_configuration
	configuration = intelliswitch_configuration
except:
	getLogger().error("IntelliSwitch: No configuration found. IntelliSwitch cannot start!!!!")
	
# Configuration found -> continue
if (configuration is not None):
	intelliSwitch = None
	try:
		intelliSwitch = IntelliSwitchManager()
		#Load configuration
		intelliSwitch.LoadConfig(configuration)
	except:
		logger.error(traceback.format_exc())

logger.info("IntelliSwitch - All Setup!")

