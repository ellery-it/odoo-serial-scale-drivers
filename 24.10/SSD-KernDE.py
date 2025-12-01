# -*- coding: utf-8 -*-
"""
Description: Serial Scale Driver for Odoo IotBox
Scale: KERN DE (Data transfer mode: Data output via remote control commands)
Author: Andrea Diaco
Github: https://github.com/ellery-it
Date: 2025-12-01
Version: 0.2
Filename: SSD-KernDE.py
License: GNU GENERAL PUBLIC LICENSE 3.0 

"""

from collections import namedtuple
import logging
import re
import serial
import threading
import time

from odoo import http
from odoo.addons.hw_drivers.controllers.proxy import proxy_drivers
from odoo.addons.hw_drivers.event_manager import event_manager
from odoo.addons.hw_drivers.iot_handlers.drivers.SerialBaseDriver import SerialDriver, SerialProtocol, serial_connection
from odoo.addons.hw_drivers.iot_handlers.drivers.SerialScaleDriver import ScaleDriver

_logger = logging.getLogger(__name__)

# Only needed to ensure compatibility with older versions of Odoo
ACTIVE_SCALE = None
new_weight_event = threading.Event()

ScaleProtocol = namedtuple('ScaleProtocol', SerialProtocol._fields + ('zeroCommand', 'tareCommand', 'clearCommand', 'autoResetWeight'))


# KERN DE
#https://www.kern-sohn.com/manuals/files/English/DE-BA-e-1356.pdf
#M-       0.000 kg
KernDEProtocol = ScaleProtocol(
    name='Kern DE (ver. 0.2)',
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    stopbits=serial.STOPBITS_ONE,
    parity=serial.PARITY_NONE,
    timeout=1,
    writeTimeout=1,
    measureRegexp=br"^[\sM][\s-]\s*([0-9.]+)\skg",             
    statusRegexp=None,
    commandDelay=0.2,
    measureDelay=0.5,
    newMeasureDelay=0.2,
    commandTerminator=b'',
    measureCommand=b'w',    #stable or unstable weigth
    zeroCommand=None,       #no zero command
    tareCommand=b't',
    clearCommand=None,      # No clear command -> Tare again
    emptyAnswerValid=False,
    autoResetWeight=False,
)





class KernDEDriver(ScaleDriver):
    """Driver for the Kern DE serial scale."""
    _protocol = KernDEProtocol
    priority = 10  # Test the supported method of this driver before ADAM


    def __init__(self, identifier, device):
        super(KernDEDriver, self).__init__(identifier, device)
        self.device_manufacturer = 'Kern'

    @classmethod
    def supported(cls, device):
        """Checks whether the device, which port info is passed as argument, is supported by the driver.

        :param device: path to the device
        :type device: str
        :return: whether the device is supported by the driver
        :rtype: bool
        """

        protocol = cls._protocol

        try:
            with serial_connection(device['identifier'], protocol, is_probing=True) as connection:
                _logger.info('Try... device %s with protocol %s' % (device, protocol.name))
                connection.write(b'w' + protocol.commandTerminator)
                time.sleep(protocol.commandDelay)
                answer = connection.read(18)
                answer_hex = answer.hex()
                _logger.info('Answer: [%s] (HEX: %s) from device %s with protocol %s' % (answer, answer_hex, device, protocol.name))
                #if answer.find(b' kg \r\n')!=-1:
                if answer.find(b' kg ')!=-1:
                    _logger.info('OK %s with protocol %s' % (device, protocol.name))
                    return True
                else:
                    _logger.info('NO MATCH for " kg \\r\\n" found in answer [%s] (HEX: %s) from device %s with protocol %s' % (answer, answer_hex, device, protocol.name))               
        except serial.serialutil.SerialTimeoutException:
            _logger.exception('Serial Timeout %s with protocol %s' % (device, protocol.name))
            pass
        except Exception:
            _logger.exception('Error while probing %s with protocol %s' % (device, protocol.name))
        return False
