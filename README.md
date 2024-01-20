# Description
[Odoo Iot Box](https://www.odoo.com/documentation/16.0/applications/productivity/iot.html) allows to connect an external scale to [Odoo](https://github.com/odoo/odoo). Unfortunately, altough infrastructure is coded to easily implement additional drivers, only drivers for two protocols are provided out-of-the-box ( Mettled Toledo 8217 and Adam AZExtra)
That's why we started to write additional drivers for Odoo Iot Box to read weigths from some other scales. 

# Supports
- Kern EOC: just reads weigth in ASK mode with Remote control instructions. Accepts weigth without taking into account if scale is in stable or unstable state (See [Kern EOC manual](https://dok.kern-sohn.com/manuals/files/English/eoc-ba-e-1920.pdf))
- Kern DE: Accepts weigth without taking into account if scale is in stable or unstable state. Need to set baud rate to 9600 and  weighing units to Kg on the scale.  (See [Kern DE manual](https://www.kern-sohn.com/manuals/files/English/DE-BA-e-1356.pdf) )
- Dini Argeo 3590. Read Stable weigth. (See [Dini Argeo Manual](https://www.bilanceonline.it/allegati/MAN_DGT_T.pdf))


# Install
*connect with ssh (i.e. putty) to Iot Box (default hostname: `raspberrypi` ) from the same LAN and login with username and password (default: pi/raspberry)*

    git clone https://github.com/ellery-it/odoo-serial-scale-drivers.git
    
*permenently copy driver(s) to the directory where is located SerialScaleDriver.py, i.e. in v. 21.10:*

    sudo mount -o rw,remount /
    sudo mount -o remount,rw /root_bypass_ramdisks
    cp odoo-serial-scale-drivers/SSD*.py /root_bypass_ramdisks/home/pi/odoo/addons/hw_drivers/iot_handlers/drivers/ 
    sudo reboot

# Test
If you have just one IoBox connect to [http://raspberrypi:8069](http://raspberrypi:8069) from the same lan where the Iot Box is connected to, and check under "scales" in the main window. 
If it doesn't work you could need to identify the IP address of your Iot Box and then connect to  `http://IOTBOX-IP-ADDRESS:8069` 
    
# Uninstall
    rm -rf odoo-serial-scale-drivers
    rm -rf /root_bypass_ramdisks/home/pi/odoo/addons/hw_drivers/_handlers/drivers/SSD*.py
    
# Notes
Scale must be powered on during the boot of Iot Box (or at least when a `sudo service odoo restart` command is sent) for the scale to be recognized
    
# Compatibility
Iot Box from Odoo 12.0 to 16.0

# Tested with
    Iot Box v. 21.10
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

    cat /var/log/odoo/odoo-server.log | grep SSD
    
## Communicate with the scale via Iot Box and test commands
*Assuming device name is /dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.2:1.0-port0 (check the correct device name in the logs or connecting to http://raspberrypi:8069)*
    
    sudo screen  /dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.2:1.0-port0 9600
    CTRL+a and then 'k' will kill a screen session (y to confirm)
*Manually send commands to the scale to read, zero, or tare (measureCommand, zeroCommand, tareCommand)*

# Disclaimer
The contents of these scripts and files are created with utmost care. Nobody does warrant the accuracy, completeness or timeliness of the content. Use of the content of the contests is at your own risk.

Although I make my best effort to maintain the contents up-to-date and accurate, I can not warrant to the adequacy, accuracy, completeness or correctness of such information.

# Donations
If you like this work and want to support, you can for example buy me a coffee [!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/elleryqueen)
