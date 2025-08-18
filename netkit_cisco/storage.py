

class StorageInfo:
    """
    Information about the storage device

    Attributes:
        name (str): The name of the storage (bootflash:)
        total_size_B (int): Total capacity of the storage in bytes
        total_free_B (int): Free/available capacity of the storage, in bytes
    """

    def __init__(self, name:str="", total_free_B:int=None, total_size_B:int=None):
        self.name = name
        self.total_size_B = total_size_B
        self.total_free_B = total_free_B
    
    def has_space(self, required_bytes:int)-> bool:
        """
        Check if the storage has enough free space for a given file.

        Args:
            required_bytes (int): Number of bytes needed.
        
        Returns:
            bool: True if there is enough free space, False if not.
        """
        return self.total_free_B >= required_bytes