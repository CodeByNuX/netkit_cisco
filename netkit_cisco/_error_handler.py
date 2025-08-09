"""
Simple logger utility used across the project to write errors to file.
"""
import logging
from datetime import datetime

class _error_handler:
    
    # configuring the logger
    logging.basicConfig(
        filename="netkit_cisco.log",
        level=logging.ERROR,
        format = "%(asctime)s [%(levelname)s] %(message)s"
    )
    @staticmethod
    def log_error(message:str):
        """
        Write an error message to the log file.

        Args:
            message(str): The message to log.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"{timestamp} [ERROR] {message}"
        # Log to file
        logging.error(message)
        # print full message w/ timestamp for immediate feedback
        print(full_message)
    
    @staticmethod
    def log_info(message:str):
        """
        Write an informational message to the log file.

        Args:
            message (str): The message to log.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"{timestamp} [INFO] {message}"
        # Log to file
        logging.info(message)
        # print full message w/ timestamp for immediate feedback
        print(full_message)