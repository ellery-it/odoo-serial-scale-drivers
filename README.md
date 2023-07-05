# Description
Additional driver for Odoo Iot Box to read weigths from KERN scales. 
# Supports
- Kern EOC (limitations: just reads weigth in ASK mode with Remote control instructions. Does not consider if weigth is stable or unstable)
- Kern DE (after setting  baud rate to 9600 and  weighing units to Kg (See kern manual https://www.kern-sohn.com/manuals/files/English/DE-BA-e-1356.pdf)


# Install
*connect to iotbox with ssh  and login with username and password (default: pi/raspberry)*
    git clone https://ellery-it@github.com/ellery-it/odoo-serial-scale-drivers.git
    
*copy driver(s) to the directory where is located SerialScaleDriver.py, i.e. in v. 21.10:*
    sudo mount -o rw,remount /
    sudo mount -o remount,rw /root_bypass_ramdisks
    cp odoo-serial-scale-drivers/SSD*.py /root_bypass_ramdisks/home/pi/odoo/addons/hw_drivers/iot_handlers/drivers/ 
    sudo reboot

# Test
    connect to  http://<IOTBOX-IP-ADDRESS>:8069 and check under "scales" in the main window
# Uninstall
    rm -rf odoo-serial-scale-drivers
    rm -rf /root_bypass_ramdisks/home/pi/odoo/addons/hw_drivers/iot_handlers/drivers/SSD*.py
    
# Notes
Scale must be powered on during the boot of IotBox for the scale to be recognized
    
# Compatibility
IotBox from odoo 12.0 to 16.0

# Tested with
    IotBox v. 21.10
    Kern EOC 60K-2 
    Kern DE 35K5DL

# Troubleshooting tips
    sudo mount -o remount,rw /
    sudo mount -o remount,rw /root_bypass_ramdisks
    nano /root_bypass_ramdisks/home/pi/odoo/addons/point_of_sale/tools/posbox/configuration/odoo.conf 
*change the log level in the Odoo configuration file to `log_level = debug` and save*

    sudo service odoo restart
    tail -f /var/log/odoo/odoo-server.log
*or*

    cat /var/log/odoo/odoo-server.log | grep SerialScale
    
## to communicate with the scale and test commands
*assuming device name is /dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.2:1.0-port0 (check the correct device name in the logs or connecting to http://<IOTBOX-IP-ADDRESS>:8069)*
    
    sudo screen  /dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.2:1.0-port0 9600
    CTRL+a and then 'k' will kill a screen session (y to confirm)


