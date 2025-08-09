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

        #track connection attempts
        self.connection_attempts += 1       
        try:

            #using _SSHTransport to open Netmiko SSH ssession            
            self._connection.connect()
            self.last_connected_at = datetime.now()
            
            # Clear any previous exception record
            self.last_exception = None
        
        except NetmikoAuthenticationException as e:
            # Store the error for reference  and log it before re-raising
            self.last_exception = str(e)
            _error_handler.log_error(f"Authentication failed for {self.ip}: {e}")
            raise 
        except NetmikoTimeoutException as e:
            # Store the timeout error and log it before re-raising
            self.last_exception = str(e)
            _error_handler.log_error(f"Timeout connecting to {self.ip}: {e}")
            raise
        except Exception as e:
            # Catch and log any other unexpected erros and raise
            self.last_exception = str(e)
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
            # Ensure _connection exits and we have a Netmiko connection object
            if not self._connection or not self._connection.connection:
                return False
            
            # using find_prompt to check for active session, raises exception if connection is broken
            self._connection.connection.find_prompt() #
            return True
        except Exception:
            # connection no longer exists
            return False
        
    def _run_command(self,command:str,expect_string:str=None,read_timeout:int=30,use_textfsm:bool=False) ->str|None:
        """
        Run a single operational (show) command via Netmiko.

        Args:
            Commannd (str): The CLI command to run
            expect_string (str): Optional regex to wait for before returning
            read_timeout (int): Seconds to wait for output before timing out.
            use_textfsm: If True and template exists, return parsed output.

        """
        try:
            # Ensure we have a live SSH session before sending the command
            if not self.is_connected:
                return None
            
            # Get the active Netmiko connection object
            conn = self._connection.connection
            # Send the command and return the output
            return conn.send_command(command,expect_string=expect_string, read_timeout=read_timeout,use_textfsm=use_textfsm)
            
        except NetmikoAuthenticationException as e:
            self.last_exception = str(e)
            _error_handler.log_error(f"Authentication error running '{command}' on {self.ip}: {e}")
            return None
        except NetmikoTimeoutException as e:
            self.last_exception = str(e)
            _error_handler.log_error(f"Authentication error running '{command}' on {self.ip}: {e}")
            return None
        except Exception as e:
            self.last_exception = str(e)
            _error_handler.log_error(f"Unexpected error running '{command}' on {self.ip}: {e}")
            return None



