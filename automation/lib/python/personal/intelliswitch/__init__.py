"""
:Author: `mr-eskildsen <https://github.com/mr-eskildsen>`_
:Version: **0.3.0**

Advanced Rule Manager package for openHAB. This software is distributed as a
community submission to the `openhab-helper-libraries <https://github.com/openhab-scripters/openhab-helper-libraries>`_.


About
-----

The name IntelliSwitch comes from merging the two words intelligent and switch. The idea is that it offers
advanced switches, where multiple rules can be used to decide wheter a specific openHAB item should be ON or OFF. 


Release Notices
---------------

Below are important instructions if you are **upgrading** weatherStationUploader from a previous version.
If you are creating a new installation, you can ignore what follows.

**PLEASE MAKE SURE THAT YOU GO THROUGH ALL STEPS BELOW WHERE IT SAYS "BREAKING CHANGE"... DON'T SKIP ANY VERSION**

    **Version 0.3.0**
        Added script as a valid condition
		Rework on config loader

	**Version 0.2.0**
        General clean up.
		Fixed problem with lat / long being swapped in call to Astro 
		

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


"""
	Version of Intelliswitch
"""
__Intelliswitch_Version__ = '0.3.0'

