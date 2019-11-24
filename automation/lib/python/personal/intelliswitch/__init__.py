"""
:Author: `mr-eskildsen <https://github.com/mr-eskildsen>`_
:Version: **0.1.0**

Multi Zone Home Alarm package for openHAB. This software is distributed as a
community submission to the `openhab-helper-libraries <https://github.com/openhab-scripters/openhab-helper-libraries>`_.


About
-----

The name intelliSwitch comes from merging the two words intelligent and switch. The idea is that it offers
advanced switches. 


Release Notices
---------------

Below are important instructions if you are **upgrading** weatherStationUploader from a previous version.
If you are creating a new installation, you can ignore what follows.

**PLEASE MAKE SURE THAT YOU GO THROUGH ALL STEPS BELOW WHERE IT SAYS "BREAKING CHANGE"... DON'T SKIP ANY VERSION**


    **Version 2.0.0**
        **BREAKING CHANGE** ideAlarm new dependency: `lucid, an openHAB 2.x jsr223 Jython helper library <https://github.com/OH-Jython-Scripters/lucid>`_.
        Review that you've setup the item groups correctly as `described in wiki <https://github.com/OH-Jython-Scripters/ideAlarm/wiki/First-Installation#define-item-groups-needed-for-persistence>`_.
        Removed dependency of `openhab2-jython <https://github.com/OH-Jython-Scripters/openhab2-jython>`_. (All openhab2-jython functionality that's needed is now found in `lucid <https://github.com/OH-Jython-Scripters/lucid>`_)
        Removed dependency of `mylib <https://github.com/OH-Jython-Scripters/mylib/>`_ (All mylib functionality that's needed is now found in `lucid <https://github.com/OH-Jython-Scripters/lucid>`_)

    **Version 1.0.0**
        Added version info string to logging.
        Added ideAlarm function `__version__()`

    **Version 0.1.0**
        Initial version.


.. admonition:: **Disclaimer**

    THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
    WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
    EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
    TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
    PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
    LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
import weakref # Using this to prevent problems with garbage collection

from org.joda.time import DateTime
from org.joda.time.format import DateTimeFormat

from core.jsr223 import scope
from core.log import logging, LOG_PREFIX

from configuration import intelliswitch_configuration as configuration

from personal.intelliswitch.logging import getLogger, LogException

#try:
#	#from personal.intelliswitch.base import BaseCore
#	from personal.intelliswitch.location import SystemLocation
#	from personal.intelliswitch.manager import RuleManager
#except:
#	LogException()


def getDateToday():
	return DateTime().withTimeAtStartOfDay()


def ParseTimeStringToDate(date, timeString):
	return DateTime.parse(
			("{}-{}-{} {}").format(date.getYear(), date.getMonthOfYear(), date.getDayOfMonth(), timeString),
			DateTimeFormat.forPattern("yyyy-MM-dd HH:mm"))
