"""
Handles SSH connections to Cisco devices using Netmiko.

This module defines the _SSHTransport class, which wraps all SSH sessions logic.
It expects a CiscoDevice object as input, from which it puls IP, credentials,
and device type to initiate the connection.

Autodetection of platform type is supported when DeviceType.AUTO_DETECT is used.
"""
from __future__ import annotations
from netmiko import ConnectHandler, ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
from netmiko.ssh_autodetect import SSHDetect
#from netkit_cisco.device import CiscoDevice
from netkit_cisco.platforms import DeviceType

class _SSHTransport:
    """
    Manages the SSH connection to a Cisco device.

    This class is initialsed with a CiscoDevice instance and uses its
    attributes to set up and manage Netmiko connection
    """
    def __init__(self,device:"CiscoDevice"):
        """
        Initialize netmiko connection parameters

        """
        self.connect_params = {
            "host": device.ip,
            "username": device.username,
            "password": device.password,
            "port": device.ssh_port,
            "device_type": device.device_type
        }

        self.connection:ConnectHandler = None
        
    def connect(self):
        """
        Establish an SSH session with the device.

        If autodetect is enabled, the correct platform will be guessed before connecting

        Returns:
            ConnectHandler: The live Netmiko SSH session
        """
        try:
            
            if self.connect_params["device_type"] == DeviceType.AUTO_DETECT.value:
                guesser = SSHDetect(**self.connect_params)
                best_match = guesser.autodetect()
                self.connect_params["device_type"] = best_match

            self.connection = ConnectHandler(**self.connect_params)
            return self.connection
        
        except NetmikoAuthenticationException:
            raise
        except NetmikoTimeoutException:
            raise
        except Exception:
            raise
