PLEASE NOTE:
============

This project contains a submodule (subproject) can-utils that must be intialized by 
executing:

	git submodule init
	git submodule update

from within the HVAC_PACKAGE_20140324/files/root/can-utils directory structure.  If you
fail to perform these two commands, you'll find that the HVAC_PACKAGE_20140324/files/root/can-utils
directory is empty!

ALso, please note that modifications to this subproject are separately maintained and
must be updated outside the main repository (e.g., updates, commits, etc to can-utils
must be done from within the HVAC_PACKAGE_20140324/files/root/can-utils tree.


INSTALLATION ON THE TARGET MACHINE:
===================================
Running the "build" command file in the root of this repository will create a zip file,
HVAC_PACKAGE_20140324.zip.

Copy the zip file to someplace on the target machine and unzip it.  It will unzip into
a directory HVAC_PACKAGE_20140324.  (If the unzip fails, try a different tool-- some
unzips are not able to handle symbolic links.)

Cd into the HVAC_PACKAGE_20140324 directory and execute the "install.sh" script file.
It should run without error.

Plug a Peak canbus interface into USB0 (lower USB jack on the front of the NDIS box)
and reboot the computer.  If all is well, the red LED on the canbus interface will
flash slowly (about once a second).

If you run the HVAC application, moving the temperature sliders should make the temperature
indicators roll, too.

