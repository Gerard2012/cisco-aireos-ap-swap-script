# cisco-aireos-ap-swap-script
Python script to help automate the bulk like-for-like replacement of wireless Access Points registered to a Cisco AireOS Wireless LAN Controller.

The script creates a .vbs file that can be used with SecureCRT with an open SSH connection to the WLC to automatically reconfigure the new APs with the setting of those they replaced.

This done by comparing the output of the "show ap cp neighbors all" command before and after the APs have been replaced.
