#!/bin/sh
# -- Copy needed config files to target
cp -f -b -r files/* /

# -- Install the driver (SHOULD be unnecessary...)
pushd /root/peak-linux-driver-7.9
# make install
popd

#
# -- This step may be necessary when "insmod pcan.ko" works but "modprobe pcan" does not:
#    Reference http://stackoverflow.com/questions/225845/how-do-i-configure-modprobe-to-find-my-module
#
depmod -a
systemctl enable pcan

# -- Install can utils
pushd /root/can-utils
make install
popd

# -- Install amb and useful tools
pushd /root/utilities
ln -t /usr/local/bin *
popd

# -- Install the HVAC application
pushd /root
wrt-installer --install intelPoc16.HVAC.wgt
popd

echo "Script complete."



