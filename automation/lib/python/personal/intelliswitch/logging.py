import inspect
import linecache
import sys
import traceback

from org.slf4j import LoggerFactory
from core.log import logging, LOG_PREFIX

#from personal.intelliswitch import LOG_NAMESPACE
from personal.intelliswitch.utils import getClassName

LOG_NAMESPACE = "{}.personal.intelliswitch".format(LOG_PREFIX)

def getLogger(namespace = LOG_NAMESPACE):
	return logging.getLogger(namespace)
	
	
class Context():
	__base_jsr_context__ = LOG_NAMESPACE
	
	def __init__(self, moduleName, className):
		self._moduleName = moduleName
		self._className = className

	def getModuleName(self):
		return self._moduleName
		
	def getClassName(self):
		return self._className
	
	def toString(self):
		moduleName = self.getModuleName()
		className = self.getClassName()
		
			
		if (moduleName is None):
			moduleName = ""
		else:
			moduleName = "." + moduleName
		
		if (className is None):
			className = ""
		else:
			className = "." + className
		
		return self.__base_jsr_context__ + moduleName + className 
		

def getContext(frame, moduleName = None):
	
	module_name = None
	class_name = None

	#ClassName
	try:
		class_name = frame.f_locals['self'].__class__.__name__
	except:
		class_name = None
	
	if (moduleName is None):
		try:
			module = inspect.getmodule(frame)
			module_name = inspect.getmodule(frame).__name__
		except:
			module_name = None
	else:
		module_name = moduleName
		
	return Context(module_name, class_name)	
	
def _getLoggerAdv(context):
	return LoggerFactory.getLogger(context.toString())
	
def getLoggerAdv(moduleName, className):
	return _getLoggerAdv( NewContext(moduleName, className) )
	
def getLogger(moduleName = None):
	return _getLoggerAdv( getContext(sys._getframe(1), moduleName) )



def LogException():
	exc_type, exc_obj, tb = sys.exc_info()
	frame = tb.tb_frame
	lineno = tb.tb_lineno
	filename = frame.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, frame.f_globals)
	context = getContext(frame)
	_getLoggerAdv(context).error(('EXCEPTION IN ({}, LINE {} "{}"): {}').format(filename, lineno, line.strip(), exc_obj))

def LogDeprecated(message):
	context = getContext(frame)
	_getLoggerAdv(context).warn('DEPRECATED {}'.format(message))
	_getLoggerAdv(context).warn(traceback.format_exc())
