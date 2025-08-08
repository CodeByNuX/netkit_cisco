"""
Defines supported Netmiko Cisco device types as an enumeration for use throughout the project.

"""
from enum import Enum

class DeviceType(str,Enum):
    """
    Represents cisco platform types for indentification and connection logic.

    These values map to what Netmiko expects for device_type.
    """
    CISCO_IOS = "cisco_ios"
    CISCO_XE =  "cisco_xe"
    CISCO_NXOS = "cisco_nxos"
    CISCO_ASA = "cisco_asa"
    AUTO_DETECT = "autodetect"