import argparse
from enum import Enum


class Protocol(Enum):
    """
    Supported blockchain protocols for the comparator.
    """
    ORDINAL = 1
    BRC20 = 2

    @staticmethod
    def from_string(value):
        """
        Convert a string to a Protocol enum value, case-insensitive.
        
        Args:
            value (str): The string representation
            
        Returns:
            Protocol: The corresponding enum value
            
        Raises:
            argparse.ArgumentTypeError: If value is not a valid protocol name
        """
        value_upper = value.upper()
        choices_upper = [e.name.upper() for e in Protocol]
        if value_upper not in choices_upper:
            raise argparse.ArgumentTypeError(f"Invalid protocol: {value}. Valid options: {', '.join([e.name for e in Protocol])}")
        return next(e for e in Protocol if e.name.upper() == value_upper) 