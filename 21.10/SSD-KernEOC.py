# -*- coding: utf-8 -*-
"""
Description: Serial Scale Driver for Odoo IotBox
Scale: KERN EOC (ASK protocol)
Author: Andrea Diaco
Github: https://github.com/ellery-it
Date: 2023-07-05
Version: 0.1
Filename: SSD-KernEOC.py
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


# KERN EOC
#https://dok.kern-sohn.com/manuals/files/Italian/KIB-TM-ZB-i-1710.pdf
#https://dok.kern-sohn.com/manuals/files/English/eoc-ba-e-1920.pdf
KernEOCProtocol = ScaleProtocol(
    name='Kern EOC (ver. 0.1)',
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    stopbits=serial.STOPBITS_ONE,
    parity=serial.PARITY_NONE,
    timeout=1,
    writeTimeout=1,
    measureRegexp=b"^[SU][TS],[NG][TS]\s*([0-9.]+)kg",             
    statusRegexp=None,
    commandDelay=0.2,
    measureDelay=0.5,
    newMeasureDelay=0.2,
    commandTerminator=b'',
    measureCommand=b'W',
    zeroCommand=b'Z',
    tareCommand=b'T',
    clearCommand=None,  # No clear command -> Tare again
    emptyAnswerValid=False,
    autoResetWeight=False,
)





class KernEOCDriver(ScaleDriver):
    """Driver for the Kern EOC serial scale."""
    _protocol = KernEOCProtocol

    def __init__(self, identifier, device):
        super(KernEOCDriver, self).__init__(identifier, device)
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
                _logger.info('Try... %s with protocol %s' % (device, protocol.name))
                connection.write(b'S' + protocol.commandTerminator)
                time.sleep(protocol.commandDelay)
                answer = connection.read(6)
                _logger.info('Answer: [%s]. %s with protocol %s' % (answer, device, protocol.name))
#                if answer == b'\xffST,GS':
#                if answer == b'ST,GS':
                if answer.find(b'ST,GS')!=-1:
#                    connection.write(b'F' + protocol.commandTerminator)  #end echo mode on MT 8217
                    _logger.info('OK %s with protocol %s' % (device, protocol.name))
                    return True
        except serial.serialutil.SerialTimeoutException:
            _logger.exception('Serial Timeout from device %s with protocol %s' % (device, protocol.name))
            pass
        except Exception:
            _logger.exception('Error while probing device %s with protocol %s' % (device, protocol.name))
        return False
