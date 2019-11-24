from abc import ABCMeta, abstractmethod
import uuid
from personal.intelliswitch.logging import getLogger, LogException


class BaseCore(object):
	__metaclass__ = ABCMeta	

	_id = ""
	_name = ""
	
	@abstractmethod
	def __init__(self, name):
		try:
			self._id = str(uuid.uuid4())
			self._name = name
		except:
			LogException()
			
	def getName(self):
		return self._name

	def getId(self):
		return self._id
