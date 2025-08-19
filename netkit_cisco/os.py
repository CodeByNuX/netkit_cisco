import re
from netkit_cisco._enums import InstallMode

class IOSXEVersion:
    """
    Represents a parsed IOS-XE version string.

    Example version strings:
        - "17.3.4"
        - "17.3.4a"

    Attributes:
        raw (str): The original version string.
        family (str): The OS family ("IOS-XE").
        major (int): The major version number (e.g., 17).
        minor (int): The minor version number (e.g., 3).
        patch (int): The patch version number (e.g., 4).
        rebuild_letter (str): Optional rebuild letter (e.g., "a").
    """

    def __init__(self, raw: str):
        self.raw = raw
        self.family = "IOS-XE"
        self.major = 0
        self.minor = 0
        self.patch = 0
        self.rebuild_letter = ""
        self.install_mode = InstallMode.UNKNOWN


        # Regex pattern matches formats like:
        #   17.3.4   or   17.3.4a
        value = re.match(r"^(\d{1,2})\.(\d{1,2})\.(\d{1,2})([a-z])?$", raw)
        if value:
            self.major = int(value.group(1))           # Capture major version
            self.minor = int(value.group(2))           # Capture minor version
            self.patch = int(value.group(3))           # Capture patch version
            self.rebuild_letter = value.group(4) or "" # Optional rebuild letter

    def is_newer_than(self, other) -> bool:
        """
        Compare this version to another IOSXEVersion object.

        Args:
            other (IOSXEVersion): The version to compare against.

        Returns:
            bool: True if this version is newer than the other.
        """
        return (self.major, self.minor, self.patch, self.rebuild_letter) > \
               (other.major, other.minor, other.patch, other.rebuild_letter)
    
    def set_install_mode(self,image_value:str) ->None:
        img = image_value.strip().lower()
        if img.endswith(".conf"):
            self.install_mode = InstallMode.INSTALL
        elif img.endswith(".bin"):
            self.install_mode = InstallMode.BUNDLE
        else:
            self.install_mode = InstallMode.UNKNOWN


class NXOSVersion:
    """
    Represents a parsed NX-OS version string.

    Example version strings:
        - "7.0(3)I7(9)"
        - "9.3(10)"
        - "10.2(3)F"

    Attributes:
        raw (str): The original version string.
        family (str): The OS family ("NX-OS").
        major (int): Major version number (e.g., 7 or 9).
        minor (int): Minor version number.
        maintenance (int): Maintenance release number inside parentheses.
        train (str): Train identifier (e.g., "I7").
        rebuild (int): Rebuild number if present (e.g., 9 in I7(9)).
        suffix (str): Optional suffix (e.g., "F" in 10.2(3)F).
    """

    def __init__(self, raw: str):
        self.raw = raw
        self.family = "NX-OS"
        self.major = 0
        self.minor = 0
        self.maintenance = 0
        self.train = ""
        self.rebuild = 0
        self.suffix = ""
        self.install_mode = InstallMode.NA # NXOS future implementation 

        # Parse I-style format: e.g., "7.0(3)I7(9)"
        value = re.match(r"^(\d+)\.(\d+)\((\d+)\)(I\d)(?:\((\d+)\))?$", raw)
        if value:
            self.major = int(value.group(1))          # Major version
            self.minor = int(value.group(2))          # Minor version
            self.maintenance = int(value.group(3))    # Maintenance release
            self.train = value.group(4)               # Train identifier (I7, etc.)
            self.rebuild = int(value.group(5)) if value.group(5) else 0
            return

        # Parse simpler format: e.g., "9.3(10)" or "10.2(3)F"
        value = re.match(r"^(\d+)\.(\d+)\((\d+)\)([A-Z])?$", raw)
        if value:
            self.major = int(value.group(1))
            self.minor = int(value.group(2))
            self.maintenance = int(value.group(3))
            self.suffix = value.group(4) or ""
            return
    def set_install_mode(self,image_value:str) -> None:
        """
        NX-OS future update
        """
        self.install_mode = InstallMode.NA #

    def is_newer_than(self, other) -> bool:
        """
        Compare this version to another NXOSVersion object.

        Args:
            other (NXOSVersion): The version to compare against.

        Returns:
            bool: True if this version is newer than the other.
        """
        return (self.major, self.minor, self.maintenance, self.train,
                self.rebuild, self.suffix) > \
               (other.major, other.minor, other.maintenance, other.train,
                other.rebuild, other.suffix)


def parse_version(raw: str):
    """
    Try to parse a raw version string into the correct class.

    Args:
        raw (str): The version string to parse.

    Returns:
        IOSXEVersion | NXOSVersion | None: A version object if parsing succeeds,
                                           otherwise None.
    """
    for cls in (IOSXEVersion, NXOSVersion):
        obj = cls(raw)
        if obj.major != 0:  # If parsing succeeded (major > 0), return the object
            return obj
    return None
