# Description
Additional driver for Odoo Iot Box to read weigths from KERN scales. 
# Supports
- Kern EOC Out of the box (limitations: just reads weigth in ASK mode with Remote control instructions. Does not consider if weigth is stable or unstable)
- Kern DE (after setting  baud rate to 9600 and  weighing units to Kg (See kern manual https://www.kern-sohn.com/manuals/files/English/DE-BA-e-1356.pdf)


# Install
    connect to iotbox with ssh  and login with standard  username and password
    sudo mount -o rw,remount /
    sudo mount -o remount,rw /root_bypass_ramdisks
    put the file in the drivers directory (the same directory where is located SerialScaleDriver.py  es.: /root_bypass_ramdisks/addons/hw_drivers/iot_handlers/drivers for iotbox from odoo 16.0 ) with an ftp over ssh client, or create a new blank file named SerialScaleDriverKernBase.py and paste contents of this file
    
# Notes
Scale must be powered on during the boot of Iot Box for the scale to be recognized
    
# Compatibility
Iot Box from odoo 8.0 to 16.0

# Tested with
    IotBox v. 21.10
    Kern EOC 60K-2 
