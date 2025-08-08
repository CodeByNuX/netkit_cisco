
from netkit_cisco.device import CiscoDevice

node = CiscoDevice("test","192.168.2.136","admin","MyPassword")

if node.ssh_connect() == False:
    print("something went wrong")
else:
    print("Yay")