# -*- coding: utf-8 -*-
"""
Description: Serial Scale Driver for Odoo IotBox
Scale: DINI ARGEO
Author: Andrea Diaco
Github: https://github.com/ellery-it
Date: 2024-01-20
Version: 0.2
Filename: SSD-DiniArgeo3590Standard.py
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


# DINI ARGEO 3590 
#https://www.bilanceonline.it/allegati/MAN_DGT_T.pdf
#https://www.manualslib.com/download/2025363/Dini-Argeo-3590ext-Series.html
DiniArgeo3590Standard = ScaleProtocol(
    name='DINI ARGEO 3590 Standard (ver. 0.2)',
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    stopbits=serial.STOPBITS_ONE,
    parity=serial.PARITY_NONE,
    timeout=1,
    writeTimeout=1,
    measureRegexp=br"^ST,1,\s*([0-9.]+)kg,\s*[0-9.]+kg",             
    statusRegexp=None,
    commandDelay=0.2,
    measureDelay=0.5,
    newMeasureDelay=0.2,
    commandTerminator=b'\r\n',
    measureCommand=b'READ',
    zeroCommand=b'ZERO',
    tareCommand=b'TARE',
    clearCommand=b'C',
    emptyAnswerValid=False,
    autoResetWeight=False,
)





class KernEOCDriver(ScaleDriver):
    """Driver for the DINI ARGEO 3590 serial scale."""
    _protocol = DiniArgeo3590Standard
    priority = 30  # Test the supported method of this driver before ADAM

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
                connection.write(b'PCOK' + protocol.commandTerminator)
                time.sleep(protocol.commandDelay)
                answer = connection.read(6)
                _logger.info('Answer: [%s]. %s with protocol %s' % (answer, device, protocol.name))
                if answer.find(b'OK')!=-1 or answer.find(b'ERR04')!=-1 : 
                    _logger.info('OK %s with protocol %s' % (device, protocol.name))
                    return True
        except serial.serialutil.SerialTimeoutException:
            _logger.exception('Serial Timeout from device %s with protocol %s' % (device, protocol.name))
            pass
        except Exception:
            _logger.exception('Error while probing device %s with protocol %s' % (device, protocol.name))
        return False
