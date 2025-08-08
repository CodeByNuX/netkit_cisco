"""
device.py

Defines the CiscoDevice class, which represents a single Cisco router or switch.

This class is desinged to model a device as an object, and manage SSH connections.
It provides access to various device attributes such as hostname, interfaces,
platform type, OS version, and availiable storage.
"""
from datetime import datetime
from netmiko import NetmikoAuthenticationException, NetmikoTimeoutException
from netkit_cisco.platforms import DeviceType
from netkit_cisco.transport.ssh import _SSHTransport
from netkit_cisco._error_handler import _error_handler

class CiscoDevice:
    """
    Represents a Cisco network device, (router, switch).

    This class models the device as an object with properties such as:
    - IP address, hostname, platform type
    - Interfaces, OS version, storage, uptime
    - methods for interaction

    A devices can be connected via SSH, and its attributes queried after connection.
    """
    def __init__(self,hostname:str=None,ip:str=None,username:str=None,password:str=None,device_type:DeviceType=DeviceType.AUTO_DETECT.value):
        """
        Initialize a CiscoDevice object.

        Args:
            hostname (str): Optional name for the device
            ip (str): IP address used for SSH access
            username (str): SSH login username.
            password (str): SSH login password.
            is_connected (bool): Track SSH connection.
            device_type (DeviceType): Platform type (IOS,NX-OS, etc)
        """
        self.hostname = hostname
        self.ip = ip
        self.username = username
        self.password = password
        self.device_type = device_type
        self.last_connected_at:datetime = None
        self.connection_attempts:int = 0
        self.last_exception:str = None
        self._connection = _SSHTransport(self)
    
    def ssh_connect(self)-> bool:
        """
        Try to establish an SSH connection to the device.

        Returns:
            bool: True if the connection succeeds.

        Raises:
            NetmikoAuthenticationException: Login failed.
            NetmikoTimeoutException: host not reachable.
            Exception: any other error during connection.
        """ 
        self.connection_attempts += 1       
        try:            
            self._connection.connect()
            self.last_connected_at = datetime.now()
            self.last_exception = None
            return True
        
        except NetmikoAuthenticationException as e:

            _error_handler.log_error(f"Authentication failed for {self.ip}: {e}")
            raise 
        except NetmikoTimeoutException as e:
            _error_handler.log_error(f"Timeout connecting to {self.ip}: {e}")
            raise
        except Exception as e:
            _error_handler.log_error(f"Unexpected error connecting to {self.ip}: {e}")
            raise
    
    def ssh_disconnect():
        pass

    @property
    def is_connected(self) -> bool:
        """

        """
        try:
            if not self._connection or not self._connection.connection:
                return False
            self._connection.connection.find_prompt() #
            return True
        except Exception:
            return False

