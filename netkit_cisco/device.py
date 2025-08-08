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
    - SSH credentials and port
    - Interfaces, OS version, storage, uptime
    - State tracking: last connection, exception and number of attempts
    - methods for interaction

    A device can be connected via SSH, and its attributes queried after connection.
    """
    def __init__(self, hostname:str=None, ip:str=None, username:str=None, password:str=None, ssh_port:int=22, device_type:DeviceType=DeviceType.AUTO_DETECT.value):
        """
        Initialize a CiscoDevice object.

        Args:
            hostname (str): Optional name for the device
            ip (str): IP address used for SSH access
            username (str): SSH login username.
            password (str): SSH login password.
            ssh_port (int): SSH port number (default is 22)
            device_type (DeviceType): Platform type (IOS,NX-OS, etc)
        
        Attributes:
            connection_attempts (int): counts the number of SSH connection attempts
            last_connected_at (datetime): Timestamp of the most recent successful connection
            last_exception (str): Stores the last connetion error, if any.
        """
        self.hostname = hostname
        self.ip = ip
        self.username = username
        self.password = password
        self.ssh_port = ssh_port
        self.device_type = device_type
        self.last_connected_at:datetime = None
        self.connection_attempts:int = 0
        self.last_exception:str = None
        self._connection = _SSHTransport(self)
    
    def ssh_connect(self):
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
        
        except NetmikoAuthenticationException as e:

            _error_handler.log_error(f"Authentication failed for {self.ip}: {e}")
            raise 
        except NetmikoTimeoutException as e:
            _error_handler.log_error(f"Timeout connecting to {self.ip}: {e}")
            raise
        except Exception as e:
            _error_handler.log_error(f"Unexpected error connecting to {self.ip}: {e}")
            raise
    
    def ssh_disconnect(self):
        """
        Close the SSH session to the device

        (Not yet implemented)
        """
        try:
            self._connection.disconnect()
        finally:
            self.last_connected_at = None

    @property
    def is_connected(self) -> bool:
        """
        Check if the device has an active SSH connection.

        Returns:
            bool: True if the SSH session is live and responsive

        """
        try:
            if not self._connection or not self._connection.connection:
                return False
            self._connection.connection.find_prompt() #
            return True
        except Exception:
            return False

