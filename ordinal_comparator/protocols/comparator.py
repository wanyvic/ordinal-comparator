"""
Comparator module for blockchain receipt comparison.

This module provides base implementation for comparing block receipts from
different protocols and blockchains.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple


class BaseComparator(ABC):
    """
    Base class for comparing block receipts from different indexers.
    """

    @abstractmethod
    def compare_block_receipts(self, primary_data: Dict[str, Any], secondary_data: Dict[str, Any]) -> Tuple[
        bool, List[str]]:
        """
        Compare block receipts from primary and secondary data sources.
        
        Args:
            primary_data: Block receipt data from the primary indexer
            secondary_data: Block receipt data from the secondary indexer
            
        Returns:
            A tuple containing:
                - Boolean indicating if the receipts match
                - List of discrepancy messages if any were found
        """
        pass

    def _normalize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the data structure to prepare for comparison.
        This method can be overridden by subclasses to handle protocol-specific normalization.

        Args:
            data: Raw data to normalize

        Returns:
            Normalized data structure
        """
        return data
