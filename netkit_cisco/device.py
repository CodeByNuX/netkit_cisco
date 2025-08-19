
from datetime import datetime
import json
from netmiko import NetmikoAuthenticationException, NetmikoTimeoutException
#from netkit_cisco.platforms import DeviceType
from netkit_cisco._enums import DeviceType
from netkit_cisco.transport.ssh import _SSHTransport
from netkit_cisco._error_handler import _error_handler
from netkit_cisco.os import parse_version
from netkit_cisco.storage import StorageInfo

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
        self.config_register = None
        self.serial = None
        self.model = None
        #self.rommon = None
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

            # _auto_discovery
            # self.auto_discovery()
        
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
     

    def _safe_get(self,source, *tuple_path, default=None, log_path=None):
        """
        Safely get a nested value from lists and dictionaries

        Traverses the provided 'source' using each step in 'tuple_path'.
        Steps can be dictionary keys or list/tuple indexes.
        If any step fails due to a missing key or out of range index, or 
        invalid type, the function will return 'default' instead of raising
        an exception

        Args:
            source (dict | list): The starting object to traverse
            *tuple_path: Variable length sequence of keys/indexes to traverse
            default (None): Value to return if traversal fails at any step. Defaults to None
            log_path: Optional string used for logging the intended access path

        Returns:
            The nested value if all steps succeed, otherwise the 'default' value 
        """
        current = source
        for index_key in tuple_path:
            try:
                current = current[index_key]
            except (KeyError, IndexError, TypeError) as e:
                if log_path:
                    _error_handler.log_info(f"_safe_get: {log_path} failed at index_key {index_key}: {e}")
                return default
        return current
            
    def auto_discovery(self):
        """
        Best effort population of basic properties from 'show version', bootflash (TextFSM)
        Logs errors instead of raising
        """
        try:
            raw = self._run_command("show version", use_textfsm=True)
            
        except Exception as e:
            _error_handler.log_error(f"_auto_discovery: 'show version' failed: {e}")
            return
        
        record = self._safe_get(raw,0,default=None,log_path="raw[0]")
        if not isinstance(record,dict):
            _error_handler.log_info("_auto_discovery: first record is not a dict, skipping")
            return

        self.hostname = self._safe_get(record,"hostname",default=None, log_path="hostname")
        self.config_register = self._safe_get(record,"config_register",default=None,log_path="config_register")
        self.model = (self._safe_get(record, "hardware",0,default=None) or # IOS-XE
                      self._safe_get(record,"platform",default=None)) # NX-OS
        self.serial = (self._safe_get(record, "serial",0, default=None) or 
                       self._safe_get(record,"serial_number", default=None))
        
        self.os = parse_version((self._safe_get(record,"os") or # NX-OS
                                 self._safe_get(record,"version"))) #IOS-XE
        self.os.set_install_mode((self._safe_get(record,"running_image",default="") or self._safe_get(record,"boot_image",default="")))
        
        # ------- show bootflash:
        
        try:
            if self.os.family == "NX-OS":
                raw = self._run_command("dir bootflash: | json")
            else:
                raw = self._run_command("dir bootflash:",use_textfsm=True)
        except Exception as e:
            _error_handler.log_error(f"_auto_discovery: 'dir bootflash:' failed: {e}")
            return

        
        #
        if self.os.family == "NX-OS":
            try:
                record = json.loads(raw.strip())
            except json.JSONDecodeError as e:
                _error_handler.log_error(f"_auto_discovery: failed to decode NX-OS JSON: {e}")
                return
            except Exception as e:
                _error_handler.log_error(f"_auto_discovery: unexpected error parsing NX-OS JSON: {e}")
                return
        else:
            record = self._safe_get(raw,0,default=None,log_path="raw[0]")
        
        if not isinstance(record,dict):
            _error_handler.log_info("_auto_discovery: first record is not a dict, skipping")
            return
        
        if self.os.family == "NX-OS":
            self.storage = StorageInfo(self._safe_get(record,"usage").split(":",1)[0],int(self._safe_get(record,"bytesfree")),int(self._safe_get(record,"bytestotal")))
        else:
            self.storage = StorageInfo(self._safe_get(record,"file_system").split(":",1)[0],int(self._safe_get(record,"total_free")),int(self._safe_get(record,"total_size")))  