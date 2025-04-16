import argparse
from enum import Enum


class Blockchain(Enum):
    """
    Supported blockchain networks for the comparator.
    """
    BITCOIN = 1
    FRACTAL = 2

    def get_first_brc20_height(self):
        """
        Get the first block height where BRC20 protocol was active.
        
        Returns:
            int: The block height
        """
        if self == Blockchain.BITCOIN:
            return 779832
        elif self == Blockchain.FRACTAL:
            return 21000
        else:
            raise ValueError(f"Unknown blockchain: {self.name}")

    def get_first_inscription_height(self):
        """
        Get the first block height where Ordinal inscriptions were active.
        
        Returns:
            int: The block height
        """
        if self == Blockchain.BITCOIN:
            return 767430
        elif self == Blockchain.FRACTAL:
            return 21000
        else:
            raise ValueError(f"Unknown blockchain: {self.name}")

    @staticmethod
    def from_string(value):
        """
        Convert a string to a Blockchain enum value, case-insensitive.
        
        Args:
            value (str): The string representation
            
        Returns:
            Blockchain: The corresponding enum value
            
        Raises:
            argparse.ArgumentTypeError: If value is not a valid blockchain name
        """
        value_upper = value.upper()
        choices_upper = [e.name.upper() for e in Blockchain]
        if value_upper not in choices_upper:
            raise argparse.ArgumentTypeError(f"Invalid blockchain: {value}. Valid options: {', '.join([e.name for e in Blockchain])}")
        return next(e for e in Blockchain if e.name.upper() == value_upper) 