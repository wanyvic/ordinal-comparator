"""
Protocol-specific implementations for the comparator.
"""

from typing import Dict, Type

from ordinal_comparator.core.blockchain import Blockchain
from ordinal_comparator.core.protocol import Protocol
from .comparator import BaseComparator
from .brc20 import BRC20Comparator
from .ordinal import OrdinalComparator

# Registry of comparators for each blockchain and protocol
COMPARATORS: Dict[Blockchain, Dict[Protocol, BaseComparator]] = {
    Blockchain.BITCOIN: {
        Protocol.BRC20: BRC20Comparator(),
        Protocol.ORDINAL: OrdinalComparator(),
    },
    Blockchain.FRACTAL: {
        Protocol.BRC20: BRC20Comparator(),
        Protocol.ORDINAL: OrdinalComparator(),
    }
}


def get_comparator(blockchain: Blockchain, protocol: Protocol) -> BaseComparator:
    """
    Get the appropriate comparator for the specified blockchain and protocol.
    
    Args:
        blockchain: The blockchain type
        protocol: The protocol type
        
    Returns:
        The appropriate comparator instance
        
    Raises:
        ValueError: If the specified blockchain or protocol is unsupported
    """
    if blockchain not in COMPARATORS:
        raise ValueError(f"Unsupported blockchain: {blockchain.name}")
        
    if protocol not in COMPARATORS[blockchain]:
        raise ValueError(f"Unsupported protocol: {protocol.name} for blockchain: {blockchain.name}")
        
    return COMPARATORS[blockchain][protocol] 