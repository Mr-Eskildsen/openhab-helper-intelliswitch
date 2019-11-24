import linecache
import sys
import traceback

from decimal import Decimal


def getClassName(instance):
	return instance.__class__.__name__

def to_decimal(val, undef_value = 0):
    try:
		s = str(val)
		if (s=="UNDEF"):
			return undef_value
		return Decimal(s.strip('"'))
    except ValueError:
        return undef_value
	
	return undef_value
	
	
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False